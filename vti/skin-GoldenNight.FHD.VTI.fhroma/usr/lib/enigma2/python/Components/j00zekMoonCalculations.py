# Embedded file name: /usr/lib/enigma2/python/Components/j00zekMoonCalculations.py
"""Functions to find the phase of the moon.

Ported from "A Moon for the Sun" (aka moontool.c), a program by the
venerable John Walker.  He used algoritms from "Practical Astronomy
With Your Calculator" by Peter Duffett-Smith, Second Edition.

For the full history of the code, as well as references to other
reading material and other entertainments, please refer to John
Walker's website,
http://www.fourmilab.ch/
(Look under the Science/Astronomy and Space heading.)

The functions of primary interest provided by this module are phase(),
which gives you a variety of data on the status of the moon for a
given date; and phase_hunt(), which given a date, finds the dates of
the nearest full moon, new moon, etc.
"""
from math import sin, cos, floor, sqrt, pi, tan, atan, pow, copysign
import bisect
import datetime
PRECISION = 0.05
NEW = 0 / 4.0
FIRST = 1 / 4.0
FULL = 2 / 4.0
LAST = 3 / 4.0
NEXTNEW = 4 / 4.0

class MoonPhase:
    """I describe the phase of the moon.
    
    I have the following properties:
        date - a DateTime instance
        phase - my phase, in the range 0.0 .. 1.0
        phase_text - a string describing my phase
        illuminated - the percentage of the face of the moon illuminated
        angular_diameter - as seen from Earth, in degrees.
        sun_angular_diameter - as seen from Earth, in degrees.
    
        new_date - the date of the most recent new moon
        q1_date - the date the moon reaches 1st quarter in this cycle
        full_date - the date of the full moon in this cycle
        q3_date - the date the moon reaches 3rd quarter in this cycle
        nextnew_date - the date of the next new moon
    """

    def __init__(self, date = datetime.datetime.now()):
        """MoonPhase constructor.
        
        Give me a date, as a datetime object."""
        self.date = get_julian_datetime(date)
        self.__dict__.update(phase(self.date))
        self.phase_text = phase_string(self.phase)

    def __getattr__(self, a):
        if a in ('new_date', 'q1_date', 'full_date', 'q3_date', 'nextnew_date'):
            self.new_date, self.q1_date, self.full_date, self.q3_date, self.nextnew_date = phase_hunt(self.date)
            return getattr(self, a)
        raise AttributeError(a)

    def __repr__(self):
        if type(self.date) is int:
            jdn = self.date
        else:
            jdn = self.date.jdn
        return '<%s(%d)>' % (self.__class__, jdn)

    def __str__(self):
        if type(self.date) is int:
            d = DateTime.DateTimeFromJDN(self.date)
        else:
            d = self.date
        s = '%s for %s, %s (%%%.2f illuminated)' % (self.__class__,
         d.strftime(),
         self.phase_text,
         self.illuminated * 100)
        return s


class AstronomicalConstants:
    epoch = 2444238.5
    ecliptic_longitude_epoch = 278.83354
    ecliptic_longitude_perigee = 282.596403
    eccentricity = 0.016718
    sun_smaxis = 149585000.0
    sun_angular_size_smaxis = 0.533128
    moon_mean_longitude_epoch = 64.975464
    moon_mean_perigee_epoch = 349.383063
    node_mean_longitude_epoch = 151.950429
    moon_inclination = 5.145396
    moon_eccentricity = 0.0549
    moon_angular_size = 0.5181
    moon_smaxis = 384401.0
    moon_parallax = 0.9507
    synodic_month = 29.53058868
    lunations_base = 2423436.0
    earth_radius = 6378.16


c = AstronomicalConstants()
fixangle = lambda a: a - 360.0 * floor(a / 360.0)
torad = lambda d: d * pi / 180.0
todeg = lambda r: r * 180.0 / pi
dsin = lambda d: sin(torad(d))
dcos = lambda d: cos(torad(d))

def phase_string(p):
    phase_strings = ((NEW + PRECISION, 'New Moon'),
     (FIRST - PRECISION, 'Waxing Crescent'),
     (FIRST + PRECISION, 'First Quarter'),
     (FULL - PRECISION, 'Waxing Gibbous'),
     (FULL + PRECISION, 'Full Moon'),
     (LAST - PRECISION, 'Waning Gibbous'),
     (LAST + PRECISION, 'Last Quarter'),
     (NEXTNEW - PRECISION, 'Waning Crescent'),
     (NEXTNEW + PRECISION, 'New Moon'))
    i = bisect.bisect([ a[0] for a in phase_strings ], p)
    print i
    return phase_strings[i][1]


def phase(phase_date = datetime.datetime.now()):
    """Calculate phase of moon as a fraction:
    
    The argument is the time for which the phase is requested,
    expressed in either a DateTime or by Julian Day Number.
    
    Returns a dictionary containing the terminator phase angle as a
    percentage of a full circle (i.e., 0 to 1), the illuminated
    fraction of the Moon's disc, the Moon's age in days and fraction,
    the distance of the Moon from the centre of the Earth, and the
    angular diameter subtended by the Moon as seen by an observer at
    the centre of the Earth."""
    if hasattr(phase_date, 'jdn'):
        day = phase_date.jdn - c.epoch
    else:
        day = phase_date - c.epoch
    N = fixangle(360 / 365.2422 * day)
    M = fixangle(N + c.ecliptic_longitude_epoch - c.ecliptic_longitude_perigee)
    Ec = kepler(M, c.eccentricity)
    Ec = sqrt((1 + c.eccentricity) / (1 - c.eccentricity)) * tan(Ec / 2.0)
    Ec = 2 * todeg(atan(Ec))
    lambda_sun = fixangle(Ec + c.ecliptic_longitude_perigee)
    F = (1 + c.eccentricity * cos(torad(Ec))) / (1 - c.eccentricity ** 2)
    sun_dist = c.sun_smaxis / F
    sun_angular_diameter = F * c.sun_angular_size_smaxis
    moon_longitude = fixangle(13.1763966 * day + c.moon_mean_longitude_epoch)
    MM = fixangle(moon_longitude - 0.1114041 * day - c.moon_mean_perigee_epoch)
    evection = 1.2739 * sin(torad(2 * (moon_longitude - lambda_sun) - MM))
    annual_eq = 0.1858 * sin(torad(M))
    A3 = 0.37 * sin(torad(M))
    MmP = MM + evection - annual_eq - A3
    mEc = 6.2886 * sin(torad(MmP))
    A4 = 0.214 * sin(torad(2 * MmP))
    lP = moon_longitude + evection + mEc - annual_eq + A4
    variation = 0.6583 * sin(torad(2 * (lP - lambda_sun)))
    lPP = lP + variation
    moon_age = lPP - lambda_sun
    moon_phase = (1 - cos(torad(moon_age))) / 2.0
    moon_dist = c.moon_smaxis * (1 - c.moon_eccentricity ** 2) / (1 + c.moon_eccentricity * cos(torad(MmP + mEc)))
    moon_diam_frac = moon_dist / c.moon_smaxis
    moon_angular_diameter = c.moon_angular_size / moon_diam_frac
    res = {'phase': fixangle(moon_age) / 360.0,
     'illuminated': moon_phase,
     'age': c.synodic_month * fixangle(moon_age) / 360.0,
     'distance': moon_dist,
     'angular_diameter': moon_angular_diameter,
     'sun_distance': sun_dist,
     'sun_angular_diameter': sun_angular_diameter}
    return res


def phase_hunt(sdate):
    """Find time of phases of the moon which surround the current date.
    
    Five phases are found, starting and ending with the new moons
    which bound the current lunation.
    """
    if not hasattr(sdate, 'jdn'):
        sdate = DateTime.DateTimeFromJDN(sdate)
    adate = sdate + DateTime.RelativeDateTime(days=-45)
    k1 = floor((adate.year + (adate.month - 1) * (1.0 / 12.0) - 1900) * 12.3685)
    nt1 = meanphase(adate, k1)
    adate = nt1
    sdate = sdate.jdn
    while 1:
        adate = adate + c.synodic_month
        k2 = k1 + 1
        nt2 = meanphase(adate, k2)
        if nt1 <= sdate < nt2:
            break
        nt1 = nt2
        k1 = k2

    phases = list(map(truephase, [k1,
     k1,
     k1,
     k1,
     k2], [0 / 4.0,
     1 / 4.0,
     2 / 4.0,
     3 / 4.0,
     0 / 4.0]))
    return phases


def meanphase(sdate, k):
    """Calculates time of the mean new Moon for a given base date.
    
    This argument K to this function is the precomputed synodic month
    index, given by:
    
                        K = (year - 1900) * 12.3685
    
    where year is expressed as a year and fractional year.
    """
    if not hasattr(sdate, 'jdn'):
        delta_t = sdate - DateTime.DateTime(1900, 1, 1, 12).jdn
        t = delta_t / 36525
    else:
        delta_t = sdate - DateTime.DateTime(1900, 1, 1, 12)
        t = delta_t.days / 36525
    t2 = t * t
    t3 = t2 * t
    nt1 = 2415020.75933 + c.synodic_month * k + 0.0001178 * t2 - 1.55e-07 * t3 + 0.00033 * dsin(166.56 + 132.87 * t - 0.009173 * t2)
    return nt1


def truephase(k, tphase):
    """Given a K value used to determine the mean phase of the new
    moon, and a phase selector (0.0, 0.25, 0.5, 0.75), obtain the
    true, corrected phase time."""
    apcor = False
    k = k + tphase
    t = k / 1236.85
    t2 = t * t
    t3 = t2 * t
    pt = 2415020.75933 + c.synodic_month * k + 0.0001178 * t2 - 1.55e-07 * t3 + 0.00033 * dsin(166.56 + 132.87 * t - 0.009173 * t2)
    m = 359.2242 + 29.10535608 * k - 3.33e-05 * t2 - 3.47e-06 * t3
    mprime = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 1.236e-05 * t3
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 2.39e-06 * t3
    if tphase < 0.01 or abs(tphase - 0.5) < 0.01:
        pt = pt + ((0.1734 - 0.000393 * t) * dsin(m) + 0.0021 * dsin(2 * m) - 0.4068 * dsin(mprime) + 0.0161 * dsin(2 * mprime) - 0.0004 * dsin(3 * mprime) + 0.0104 * dsin(2 * f) - 0.0051 * dsin(m + mprime) - 0.0074 * dsin(m - mprime) + 0.0004 * dsin(2 * f + m) - 0.0004 * dsin(2 * f - m) - 0.0006 * dsin(2 * f + mprime) + 0.001 * dsin(2 * f - mprime) + 0.0005 * dsin(m + 2 * mprime))
        apcor = True
    elif abs(tphase - 0.25) < 0.01 or abs(tphase - 0.75) < 0.01:
        pt = pt + ((0.1721 - 0.0004 * t) * dsin(m) + 0.0021 * dsin(2 * m) - 0.628 * dsin(mprime) + 0.0089 * dsin(2 * mprime) - 0.0004 * dsin(3 * mprime) + 0.0079 * dsin(2 * f) - 0.0119 * dsin(m + mprime) - 0.0047 * dsin(m - mprime) + 0.0003 * dsin(2 * f + m) - 0.0004 * dsin(2 * f - m) - 0.0006 * dsin(2 * f + mprime) + 0.0021 * dsin(2 * f - mprime) + 0.0003 * dsin(m + 2 * mprime) + 0.0004 * dsin(m - 2 * mprime) - 0.0003 * dsin(2 * m + mprime))
        if tphase < 0.5:
            pt = pt + 0.0028 - 0.0004 * dcos(m) + 0.0003 * dcos(mprime)
        else:
            pt = pt + -0.0028 + 0.0004 * dcos(m) - 0.0003 * dcos(mprime)
        apcor = True
    if not apcor:
        raise ValueError('TRUEPHASE called with invalid phase selector', tphase)
    return DateTime.DateTimeFromJDN(pt)


def kepler(m, ecc):
    """Solve the equation of Kepler."""
    epsilon = 1e-06
    m = torad(m)
    e = m
    while 1:
        delta = e - ecc * sin(e) - m
        e = e - delta / (1.0 - ecc * cos(e))
        if abs(delta) <= epsilon:
            break

    return e


def get_julian_datetime(date):
    """
    based on the the Navy's Astronomical Equation found here and verified
        with their own calculator: http://aa.usno.navy.mil/faq/docs/JD_Formula.php
     Convert a datetime object into julian float.
    Args:
        date: datetime-object of date in question
    
    Returns: float - Julian calculated datetime.
    Raises: 
        TypeError : Incorrect parameter type
        ValueError: Date out of range of equation
    """
    if not isinstance(date, datetime.datetime):
        raise TypeError('Invalid type for parameter "date" - expecting datetime')
    elif date.year < 1801 or date.year > 2099:
        raise ValueError('Datetime must be between year 1801 and 2099')
    julian_datetime = 367 * date.year - int(7 * (date.year + int((date.month + 9) / 12.0)) / 4.0) + int(275 * date.month / 9.0) + date.day + 1721013.5 + (date.hour + date.minute / 60.0 + date.second / pow(60, 2)) / 24.0 - 0.5 * copysign(1, 100 * date.year + date.month - 190002.5) + 0.5
    return julian_datetime


if __name__ == '__main__':
    m = MoonPhase()
    s = 'The moon is %s (%s), %.1f%% illuminated, %.1f days old.' % (m.phase_text,
     m.phase,
     m.illuminated * 100,
     m.age)
    print s