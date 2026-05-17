"""Shared utilities for generating IFC4X3_ADD2 semantic alignment test cases."""
import pathlib
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.aggregate
import ifcopenshell.api.spatial
import ifcopenshell.api.alignment as align_api

RAIL_HEAD_DISTANCE = 1.5  # metres, standard gauge approximation

# Scale factors: multiply a metre value by this to get the equivalent in each unit.
# 1 US survey foot  = 1200/3937 m  (exact)
# 1 international foot = 0.3048 m  (exact)
UNIT_SYSTEMS = {
    'Meter':      1.0,
    'SurveyFoot': 3937.0 / 1200.0,
    'IntlFoot':       1.0 / 0.3048,
}

CURVE_FOLDER = {
    'CLOTHOID':          'Clothoid',
    'BLOSSCURVE':        'BlossCurve',
    'COSINECURVE':       'CosineCurve',
    'HELMERTCURVE':      'HelmertCurve',
    'SINECURVE':         'SineCurve',
    'VIENNESEBEND':      'VienneseBend',
    'LINE':              'Line',
    'CIRCULARARC':       'CircularArc',
    'CONSTANTGRADIENT':  'ConstantGradient',
    'PARABOLICARC':      'ParabolicArc',
    'CONSTANTCANT':      'ConstantCant',
    'LINEARTRANSITION':  'LinearTransition',
}


def _make_length_unit(ifc, unit_system):
    """Return the IfcUnit entity for the project length unit."""
    if unit_system == 'Meter':
        return ifcopenshell.api.unit.add_si_unit(ifc, unit_type='LENGTHUNIT')
    if unit_system == 'IntlFoot':
        return ifcopenshell.api.unit.add_conversion_based_unit(ifc, name='foot')

    # SurveyFoot: ifcopenshell's add_conversion_based_unit may not know this unit.
    # Probe a foot unit to discover the concrete entity type used for ValueComponent
    # (IfcMeasureWithUnit.ValueComponent is a SELECT — a plain float is rejected),
    # then build the survey foot unit with the correct factor using the same type.
    # Reuse the probe's IfcDimensionalExponents rather than creating a new one so
    # the file contains exactly one IfcDimensionalExponents (matching the IntlFoot path).
    probe     = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name='foot')
    vc_type   = probe.ConversionFactor.ValueComponent.is_a()
    si_metre  = probe.ConversionFactor.UnitComponent
    dim       = probe.Dimensions
    probe_mwu = probe.ConversionFactor
    ifc.remove(probe)
    ifc.remove(probe_mwu)

    sv_value = ifc.create_entity(vc_type, 1200.0 / 3937.0)   # 1 US survey foot in metres
    mwu = ifc.create_entity('IfcMeasureWithUnit', sv_value, si_metre)
    return ifc.create_entity('IfcConversionBasedUnit', dim, 'LENGTHUNIT', 'US SURVEY FOOT', mwu)


def setup(alignment_name, include_vertical=False, include_cant=False,
          unit_system='Meter'):
    """Create an IFC file with project, site, and empty alignment layouts.

    Per CT 4.1.5.1, IfcAlignment is aggregated to IfcProject (handled by
    align_api.create) and referenced into the spatial structure of IfcSite
    via IfcRelReferencedInSpatialStructure.

    Returns (ifc, alignment). Callers retrieve layouts via align_api.get_*_layout().
    All dimensional values written to the file must already be in project units;
    callers are responsible for scaling from metres using UNIT_SYSTEMS[unit_system].
    """
    scale = UNIT_SYSTEMS[unit_system]
    ifc = ifcopenshell.file(schema='IFC4X3_ADD2')
    ifc.header.file_description.description = ['ViewDefinition [Alignment-basedView]']
    project = ifcopenshell.api.root.create_entity(ifc, ifc_class='IfcProject', name='Alignment Test')
    length_unit = _make_length_unit(ifc, unit_system)
    radian = ifcopenshell.api.unit.add_si_unit(ifc, unit_type='PLANEANGLEUNIT')
    ifcopenshell.api.unit.assign_unit(ifc, units=[length_unit, radian])
    model_context = ifcopenshell.api.context.add_context(ifc, context_type='Model')
    ifcopenshell.api.context.add_context(
        ifc,
        context_type='Model',
        context_identifier='Axis',
        target_view='MODEL_VIEW',
        parent=model_context,
    )
    site = ifcopenshell.api.root.create_entity(ifc, ifc_class='IfcSite', name='Test Site')
    ifcopenshell.api.aggregate.assign_object(ifc, products=[site], relating_object=project)
    # IfcProject must exist before this call. align_api.create() detects it and
    # automatically aggregates the alignment to the project via IfcRelAggregates.
    alignment = align_api.create(
        ifc,
        name=alignment_name,
        include_vertical=include_vertical,
        include_cant=include_cant,
        include_geometry=False
    )
    # Reference alignment into spatial structure per CT 4.1.5.1
    ifcopenshell.api.spatial.reference_structure(ifc, products=[alignment], relating_structure=site)
    if include_cant:
        align_api.get_cant_layout(alignment).RailHeadDistance = RAIL_HEAD_DISTANCE * scale
    return ifc, alignment


def add_h_segment(ifc, layout, start_r, end_r, length, ptype,
                  start_point=(0.0, 0.0), start_direction=0.0):
    """Append one IfcAlignmentHorizontalSegment to layout.

    start_r / end_r   : signed radius in project units; 0.0 = infinite (straight),
                        positive = left curve, negative = right curve.
    start_point       : (x, y) coordinates of the segment start in project units.
    start_direction   : bearing at the segment start in radians.

    Returns the 4×4 end-placement matrix from create_layout_segment so callers
    can chain segments: extract (x, y) from column 4 rows 0–1 and direction via
    atan2(m[1,0], m[0,0]), then pass them as start_point/start_direction to the
    next call.
    """
    params = ifc.create_entity(
        'IfcAlignmentHorizontalSegment',
        StartPoint=ifc.create_entity('IfcCartesianPoint', Coordinates=start_point),
        StartDirection=start_direction,
        StartRadiusOfCurvature=start_r,
        EndRadiusOfCurvature=end_r,
        SegmentLength=length,
        PredefinedType=ptype,
    )
    return align_api.create_layout_segment(ifc, layout, params)


def add_v_segment(ifc, layout, dist_along, h_length, start_height, start_grad, end_grad, ptype):
    """Append one IfcAlignmentVerticalSegment to layout.

    Gradients are dimensionless decimal values (e.g. 0.005 for 0.5 %) — not scaled.

    Returns the 4×4 end-placement matrix from create_layout_segment so callers
    can chain segments: extract dist_along from m[0,3]/unit_scale, start_height
    from m[1,3]/unit_scale, and start_grad from m[1,0]/m[0,0].
    """
    params = ifc.create_entity(
        'IfcAlignmentVerticalSegment',
        StartDistAlong=dist_along,
        HorizontalLength=h_length,
        StartHeight=start_height,
        StartGradient=start_grad,
        EndGradient=end_grad,
        PredefinedType=ptype,
    )
    return align_api.create_layout_segment(ifc, layout, params)


def add_c_segment(ifc, layout, dist_along, h_length, scl, ecl, scr, ecr, ptype):
    """Append one IfcAlignmentCantSegment to layout.

    scl/ecl : start/end cant on left rail (project units).
    scr/ecr : start/end cant on right rail (project units).

    Returns the 4×4 end-placement matrix from create_layout_segment so callers
    can chain segments: extract dist_along from m[0,3]/unit_scale, deviating
    elevation from m[1,3]/unit_scale, and cross-slope angle from the Axis vector.
    """
    params = ifc.create_entity(
        'IfcAlignmentCantSegment',
        StartDistAlong=dist_along,
        HorizontalLength=h_length,
        StartCantLeft=scl,
        EndCantLeft=ecl,
        StartCantRight=scr,
        EndCantRight=ecr,
        PredefinedType=ptype,
    )
    return align_api.create_layout_segment(ifc, layout, params)


def write_ifc(ifc, output_dir, filename):
    """Write ifc to output_dir/filename, creating directories as needed."""
    path = pathlib.Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    dest = path / filename
    ifc.write(str(dest))
    return dest
