# Hand Calculations: Point Q for Figure 1 and Figure 2

These calculations reproduce the position of the offset point $Q$ used in Figure 1 and Figure 2, working from the basis curve definition through to the final coordinates. Both figures share the same basis curve, reference point $P$, and lateral direction; they differ in how the vertical direction $\hat v$ is defined, and consequently in how the longitudinal direction $\hat\ell$ must be defined to preserve orthogonality.

---

## 1. Given data

**Basis curve** (horizontal circular arc of radius $R$, constant grade $g$):

$$
x(s) = R\sin\left(\frac{s}{R}\right), \qquad
y(s) = R\left(1-\cos\left(\frac{s}{R}\right)\right), \qquad
z(s) = g\,s
$$

with

$$
R = 220, \qquad g = 0.45, \qquad s_0 = 170
$$

**Applied offsets** (per the spec's order of operations — lateral and vertical first, longitudinal last):

$$
\Delta_{\text{lat}} = -35, \qquad \Delta_{\text{vert}} = 25, \qquad \Delta_{\text{long}} = 15
$$

---

## 2. Reference point $P$

$$
\theta_0 = \frac{s_0}{R} = \frac{170}{220} = 0.772727
$$

$$
\cos\theta_0 = 0.716009, \qquad \sin\theta_0 = 0.698091
$$

$$
P = \big(R\sin\theta_0,\; R(1-\cos\theta_0),\; g s_0\big)
= (153.580,\; 62.478,\; 76.500)
$$

---

## 3. Tangent $T$

Differentiating the curve with respect to $s$:

$$
\frac{d}{ds}(x,y,z) = \big(\cos\theta_0,\ \sin\theta_0,\ g\big)
$$

Since $\cos^2\theta_0 + \sin^2\theta_0 = 1$, the un-normalized tangent has length

$$
n = \sqrt{1+g^2} = \sqrt{1+0.45^2} = \sqrt{1.2025} = 1.096586
$$

$$
T = \frac{1}{n}\big(\cos\theta_0,\ \sin\theta_0,\ g\big)
= (0.652944,\ 0.636604,\ 0.410365)
$$

---

## 4. Lateral direction (same in both figures)

The horizontal projection of $T$, $T_h = (\cos\theta_0, \sin\theta_0, 0)$, is already a unit vector (since $\cos^2\theta_0+\sin^2\theta_0=1$). Rotating it $90°$ counter-clockwise in the $XY$ plane gives the "left" direction:

$$
\text{Lat} = (-\sin\theta_0,\ \cos\theta_0,\ 0) = (-0.698091,\ 0.716009,\ 0)
$$

This vector has zero $z$-component by construction — it is parallel to the global $XY$ plane in **both** Figure 1 and Figure 2.

---

## 5. Vertical direction $\hat v$ — where the two figures diverge

### Figure 1: $\hat v \perp T$, within the plane of $T$ that is $\perp$ global $XY$

$$
\hat v_1 = \hat Z - (\hat Z\cdot T)\,T
$$

Since $\hat Z \cdot T = g/n$, this simplifies (using $n^2 = 1+g^2$) to the closed form:

$$
\hat v_1 = \frac{1}{n}\big(-g\cos\theta_0,\ -g\sin\theta_0,\ 1\big)
= (-0.293825,\ -0.286472,\ 0.911922)
$$

### Figure 2: $\hat v = $ global $Z$, longitudinal direction corrected to stay horizontal

$$
\hat v_2 = (0,\ 0,\ 1)
$$

Since $\hat v_2$ is global $Z$, using the full 3D tangent $T$ for the longitudinal direction would **not** be orthogonal to $\hat v_2$ (because $T$ has a $z$-component of $g/n \neq 0$). To preserve mutual orthogonality of Lateral/Vertical/Longitudinal, Figure 2 instead uses the **horizontal projection of the tangent**, $T_h$, for `OffsetLongitudinal`:

$$
T_h = (\cos\theta_0,\ \sin\theta_0,\ 0) = (0.716009,\ 0.698091,\ 0)
$$

Note $T_h$ is already a unit vector, since $\cos^2\theta_0+\sin^2\theta_0=1$. With this choice,

$$
T_h \cdot \text{Lat} = 0, \qquad T_h \cdot \hat v_2 = 0, \qquad \text{Lat} \cdot \hat v_2 = 0
$$

so $(T_h,\ \text{Lat},\ \hat v_2)$ form a proper orthogonal triad — the same property Figure 1's $(T,\ \text{Lat},\ \hat v_1)$ triad has, just built from different vectors.

---

## 6. Apply the offsets in spec order

Per the spec, lateral and vertical offsets are applied first (order between them doesn't matter, since both are added as independent vectors to $P$); the longitudinal offset is applied **last**, along the relevant longitudinal direction $\hat\ell$, from the resulting intermediate point.

$$
P_a = P + \Delta_{\text{lat}}\cdot \text{Lat}
$$

$$
P_b = P_a + \Delta_{\text{vert}}\cdot \hat v
$$

$$
Q = P_b + \Delta_{\text{long}}\cdot \hat\ell
$$

where $\hat\ell = T$ for Figure 1, and $\hat\ell = T_h$ for Figure 2 (see §5 above for why Figure 2 uses $T_h$ instead of $T$).

### Figure 1 ($\hat v = \hat v_1$)

$$
P_a = (153.580,\ 62.478,\ 76.500) + (-35)(-0.698091,\ 0.716009,\ 0)
$$
$$
P_a = (178.013,\ 37.418,\ 76.500)
$$

$$
P_b = (178.013,\ 37.418,\ 76.500) + (25)(-0.293825,\ -0.286472,\ 0.911922)
$$
$$
P_b = (170.667,\ 30.256,\ 99.298)
$$

$$
Q = (170.667,\ 30.256,\ 99.298) + (15)(0.652944,\ 0.636604,\ 0.410365)
$$

$$
\boxed{Q_{\text{Fig.1}} = (180.5,\ 39.8,\ 105.5)}
$$

### Figure 2 ($\hat v = \hat v_2$, $\hat\ell = T_h$)

$$
P_a = (153.580,\ 62.478,\ 76.500) + (-35)(-0.698091,\ 0.716009,\ 0)
$$
$$
P_a = (178.013,\ 37.418,\ 76.500) \quad \text{(identical to Figure 1 — Lat is unchanged)}
$$

$$
P_b = (178.013,\ 37.418,\ 76.500) + (25)(0,\ 0,\ 1)
$$
$$
P_b = (178.013,\ 37.418,\ 101.500)
$$

$$
Q = (178.013,\ 37.418,\ 101.500) + (15)(0.716009,\ 0.698091,\ 0)
$$

$$
\boxed{Q_{\text{Fig.2}} = (188.8,\ 47.9,\ 101.5)}
$$

---

## 7. Why the two results differ

$P_a$ is identical in both cases, since the lateral step doesn't involve $\hat v$ or $\hat\ell$ at all. From $P_b$ onward the two figures diverge in two ways: the vertical step moves partly sideways in Figure 1 (since $\hat v_1$ is tilted off true vertical to stay perpendicular to the sloped tangent $T$) but purely upward in Figure 2; and the longitudinal step covers slightly more horizontal ground in Figure 2, since $T_h$ is a unit vector while $T$'s horizontal component is shortened by the factor $1/n$ (some of $T$'s "length" goes into its $z$-component instead). Combined:

$$
Q_{\text{Fig.1}} - Q_{\text{Fig.2}} = (-8.3,\ -8.1,\ 4.0)
$$
