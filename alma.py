#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# $Id: alma.py,v 1.30 2009/11/30 18:28:38 kent Exp $
# Svenska almanackan
# Copyright 2004 Kent Engstr�m. Released under GPL.

import math
from cStringIO import StringIO

import jddate; JD=jddate.FromYMD

#
# Data
#

# M�nader (index 1..12)
month_names =   [None,
		 "Januari", "Februari", "Mars",
		 "April", "Maj", "Juni",
		 "Juli", "Augusti", "September",
		 "Oktober", "November", "December"]

# Veckodagar (index 1..7)
wday_names = [None, "M�ndag", "Tisdag", "Onsdag",
	      "Torsdag", "Fredag", "L�rdag", "S�ndag"]

# Klasser av dagar (uppdelning enligt intresse nedan �r s�klart v�ldigt godtycklig)

MRED   = 0 # R�d dag, av mera allm�nt intresse (t.ex. juldagen)
RED    = 1 # R�d dag, ej av allm�nt intresse (t.ex. doms�ndagen)
MBLACK = 2 # Svart dag, av mera allm�nt intresse (t.ex. julafton)
BLACK  = 3 # Svart dag, ej av allm�nt intresse (t.ex. allhelgondagen)

# Tidszon (positivt �t �ster)
TIMEZONE = 1

#
# Funktioner
#

# Ber�kna vilken dag som �r p�sks�ndag ett visst �r 
# Algoritm: Meeus, Jean, Astronomical Formulae for Calculators, 2 ed, s 31

def easter_sunday(year):
    a = year % 19
    b , c = divmod(year, 100)
    d , e = divmod(b, 4)
    f = (b+8) / 25
    g = (b-f+1) / 3
    h = (19*a+b-d-g+15) % 30
    i, k = divmod(c, 4)
    l = (32+2*e+2*i-h-k) % 7
    m = (a+11*h+22*l) / 451
    n, p = divmod(h+l-7*m+114, 31)

    # Formeln ovan �r gjord f�r den gregorianska kalendern.
    # Konverteringar g�rs f�r att omvandla ifall det �r den
    # svenska kalendern eller julianska kalendern:

    # Plockar ut JD utifr�n v�rt gregorianska datum:
    jd = jddate.ymd_to_jd_gregorian(year,n,p+1)

    # Plockar fram datum f�r den kalender som r�kar g�lla vid jd:
    # year �ndras inte, d� p�sks�ndagen aldrig �r n�ra ny�r:
    
    (year,month,day) = jddate.jd_to_ymd(jd)
    
    return JD(year, month, day)

# Ber�kna JD d� en viss m�nfas intr�ffar i en viss cykel
# Algoritm: Meeus, Jean, Astronomical Formulae for Calculators, 2 ed, s 159


def moonphase(cycle, phase):
    # Ber�kna parametrar
    # phase: 0 �r nym�ne, 1 �r v�xande halvm�ne, 2 �r fullm�ne, 3 �r avtagande halvm�ne
    assert phase in [0,1,2,3]
    k = cycle + phase/4.0
    t  = k / 1236.85

    # Ber�kna ursprunglig "gissning"

    jd = 2415020.75933 \
	+ 29.53058868 * k \
	+ 0.0001178 * t*t \
	- 0.000000155 * t*t*t \
	+ 0.00033 * math.sin(2.90702 + 2.31902 * t + 0.0001601 * t*t)

    # Ber�kna positioner vid denna tidpunkt

    m  = 359.2242 +  29.10535608 * k - 0.0000333 * t*t - 0.00000347 * t*t*t
    mp = 306.0253 + 385.81691806 * k + 0.0107306 * t*t + 0.00001236 * t*t*t
    f  =  21.2964 + 390.67050646 * k - 0.0016528 * t*t - 0.00000239 * t*t*t
    m  *=  math.pi/180.0
    mp *=  math.pi/180.0
    f  *=  math.pi/180.0

    # Korrigera "gissningen" m a p dessa positioner

    if phase in [0, 2]: 
	# Nym�ne och fullm�ne
	jd += (0.1734 - 0.000393*t) * math.sin(m) \
	    + 0.0021 * math.sin(2*m) \
	    - 0.4068 * math.sin(mp) \
	    + 0.0161 * math.sin(2*mp) \
	    - 0.0004 * math.sin(3*mp) \
	    + 0.0104 * math.sin(2*f) \
	    - 0.0051 * math.sin(m+mp) \
	    - 0.0074 * math.sin(m-mp) \
	    + 0.0004 * math.sin(2*f+m) \
	    - 0.0004 * math.sin(2*f-m) \
	    - 0.0006 * math.sin(2*f+mp) \
	    + 0.0010 * math.sin(2*f-mp) \
	    + 0.0005 * math.sin(m+2*mp)
    else:
	# V�xande och avtagande halvm�ne
	  jd += (0.1721 - 0.0004*t) * math.sin(m) \
	      + 0.0021 * math.sin(2*m) \
	      - 0.6280 * math.sin(mp) \
	      + 0.0089 * math.sin(2*mp) \
	      - 0.0004 * math.sin(3*mp) \
	      + 0.0079 * math.sin(2*f) \
	      - 0.0119 * math.sin(m+mp) \
	      - 0.0047 * math.sin(m-mp) \
	      + 0.0003 * math.sin(2*f+m) \
	      - 0.0004 * math.sin(2*f-m) \
	      - 0.0006 * math.sin(2*f+mp) \
	      + 0.0021 * math.sin(2*f-mp) \
	      + 0.0003 * math.sin(m+2*mp) \
	      + 0.0004 * math.sin(m-2*mp) \
	      - 0.0003 * math.sin(2*m+mp)

	  if phase == 1:
	      jd += 0.0028 - 0.0004*math.cos(m) + 0.0003*math.cos(mp);
	  else:
	      jd -= (0.0028 - 0.0004*math.cos(m) + 0.0003*math.cos(mp));

    # Korrigera f�r:
    # 1) Resten av programmet har en lite annorlunda definition av JD.
    #    JD h�r = JD i resten - 0.5 dygn
    #  2) Tidszon

    jd = jd + 0.5 + TIMEZONE/24.0

    # Dela upp i dag, timme, minut

    day  = int(jd)
    rest = (jd - day) * 24
    hour = int(rest)
    min  = int((rest - hour) * 60);

    # �terv�nd med datumtyp, kasta tillsvidare h och m
    return jddate.FromJD(day)


# F�rsta veckodagen av visst slag p� eller efter ett visst datum
def first_weekday(y, m, d, wd):
    jd = JD(y, m, d)
    (_, _, jdwd) = jd.GetYWD()
    diff = wd - jdwd
    if diff < 0: diff = diff + 7
    return jd + diff

def first_sunday(y, m, d):
    return first_weekday(y, m, d, 7)

def first_saturday(y, m, d):
    return first_weekday(y, m, d, 6)

# F�reg�ende m�nad
def previous_month(y, m):
    if m == 1:
	return (y-1, 12)
    else:
	return (y, m-1)

# N�sta m�nad
def next_month(y, m):
    if m == 12:
	return (y+1, 1)
    else:
	return (y, m+1)

# F�reg�ende vecka
def previous_week(y, w):
    jd = jddate.FromYWD(y, w, 1) - 7
    y, w, _ = jd.GetYWD()
    return y, w

# N�sta vecka
def next_week(y, w):
    jd = jddate.FromYWD(y, w, 1) + 7
    y, w, _ = jd.GetYWD()
    return y, w

# �r och vecka --> �r och m�nad
# (f�rsta dagen i veckan f�r best�mma)
def yw_to_ym(year, week):
    jd = jddate.FromYWD(year, week, 1)
    year, month, _ = jd.GetYMD()
    return year, month

# �r och m�nad --> �r och vecka
# (f�rsta dagen i m�naden f�r best�mma)
def ym_to_yw(year, month):
    jd = jddate.FromYMD(year, month, 1)
    year, week, _ = jd.GetYWD()
    return year, week


#
# Klasser
#

class DayName:
    """Class to represent a day name and its importance."""
    def __init__(self, name, dayclass):
	self.name = name
	self.dayclass = dayclass
	self.is_red = dayclass <= RED

    def __repr__(self):
	return "<%s %d>" % (self.name, self.dayclass)

class DayCal:
    """Class to represent a single day."""
    def __init__(self, jd, mark_as_today = False):
	self.jd = jd           # jddate
        self.is_today = mark_as_today

	(self.y,
	 self.m,
	 self.d) = self.jd.GetYMD()

	(self.wyear,
	 self.week,
	 self.wday) = self.jd.GetYWD()

	# wday �r alltid 1 f�r m�ndag ... 7 f�r s�ndag
	# wpos talar om positionen i veckan
	if self.y >= 1973:
	    self.wpos = self.wday # m�ndag f�rst i veckan
	else:
	    if self.wday == 7:
		self.wpos = 1 # s�ndag f�rst i veckan
	    else:
		self.wpos = self.wday + 1

	self.flag_day = False  # flaggdag?
	self.day_names = []    # r�da och svarta dagsnamn, blandat (klass DayName)
	self.names = []        # namnsdagsnamn
	self.wday_name = wday_names[self.wday]
	self.wday_name_short = self.wday_name[:3]

	if self.wday == 7:
	    self.red = True    # Alla s�ndagar �r r�da
	else:
	    self.red = False   # Alla andra dagar �r svarta tillsvidare

	self.moonphase = None  # M�nfas (0 = nym�ne, 1, 2 = fullm�ne, 3)
 
    def add_info(self, dayclass, flag, name):
	assert MRED <= dayclass <= BLACK
	if dayclass <= RED:
	    self.red = True
	if name: self.day_names.append(DayName(name, dayclass))
	if flag:
	    self.flag_day = True
    
    def set_names(self, names):
	self.names = names

    def set_moonphase(self, moonphase):
	self.moonphase = moonphase

    def moonphase_name(self):
	if self.moonphase is None:
	    return ""
	else:
	    return ["Nym�ne", "F�rsta kvarteret", "Fullm�ne", "Sista kvarteret"][self.moonphase]

    def __repr__(self):
	return "<Day %s>"  % self.jd.GetString_YYYY_MM_DD()

    def html_redblack(self, sep = ", "):
	redblack = []
	for dayclass in range(MRED,BLACK+1):
	    for dayname in self.day_names:
		if dayname.dayclass == dayclass:
		    if dayname.is_red:
			colour = "red"
		    else:
			colour = "black"
		    redblack.append('<SPAN CLASS="vname %s">%s</SPAN>' % (colour, dayname.name))
	return sep.join(redblack)

    def html_vertical(self, f, in_week_cal = False, for_printing = False):
	if self.red:
	    colour = "red"
	else:
	    colour = "black"

        if self.is_today and not for_printing:
            f.write('<TR CLASS="v today">')
        else:
            f.write('<TR CLASS="v">')

	# Veckan b�rjar p� m�ndag fr o m 1973, innan p� m�ndag
	# Dessutom "b�rjar" ju en vecka i b�rjan av varje m�nad.
	if self.d == 1 or self.wpos == 1:
            if in_week_cal:
                # I en veckokalender �r det ju m�naden som �r intressant
                wtext = '<A CLASS="hidelink" HREF="?year=%d&month=%d&type=vertical">%s</A>' % (self.y,
                                                                                               self.m,
                                                                                               month_names[self.m][:3])
            else:
                # I m�nadskalender vill vi ha veckonumret
                if self.y >= 1973:
                    # Veckonummer relevant fr o m 1973
                    wtext = '<A CLASS="hidelink" HREF="?year=%d&week=%d&type=week">%s</A>' % (self.wyear,
                                                                                              self.week,
                                                                                              self.week)
                else:
                    wtext = "&nbsp;"
	    f.write('<TD CLASS="vweek_present leftmost">%s</TD>' % wtext)
	else:
	    f.write('<TD CLASS="vweek_empty leftmost">&nbsp;</TD>')

	# Veckodagens tre f�rst tecken
	f.write('<TD CLASS="vwday %s">%s</TD>' % (colour, self.wday_name_short))

	# Dagens nummer
	f.write('<TD CLASS="vday %s">%d</TD>' % (colour, self.d))

	# Flaggdagar och m�nfaser
	f.write('<TD CLASS="vflag">')
	empty = True

	if self.flag_day:
	    f.write('<IMG SRC="flag.gif" ALT="Flaggdag" TITLE="Flaggdag">')
	    empty = False

	if self.moonphase is not None:
	    f.write('<IMG SRC="moonphase%d.gif" ALT="%s" TITLE="%s">' % (self.moonphase, self.moonphase_name(), self.moonphase_name()))
	    empty = False

	if empty:
	    f.write('&nbsp;')
	f.write('</TD>')

	# Dagens namn. �verst r�da, svarta. Under namnsdagar
	redblack_string = self.html_redblack()
	name_string = ", ".join(self.names)
	
	if in_week_cal:
            f.write('<TD CLASS="vnames">')
        else:
            f.write('<TD CLASS="vnames rightmost">')
	f.write(redblack_string)
	if redblack_string and name_string: f.write('<BR>')
	f.write(name_string)
	f.write('&nbsp;</TD>')

        # Anteckningsutrymme i veckoalmanackan
        if in_week_cal:
            f.write('<TD CLASS="vnotes rightmost">&nbsp;</TD>')


	f.write('</TR>\n')

    def html_tabular(self, f, for_printing = False, high = False):
	if self.red:
	    colour = "red"
	else:
	    colour = "black"
	
        if self.is_today and not for_printing:
            f.write('<TD CLASS="tday today">')
        else:
            f.write('<TD CLASS="tday">')
	f.write('<TABLE>')

	# Dagens nummer
	f.write('<TR><TD CLASS="tdday %s">%d</TD>' % (colour, self.d))

	# Dagens namn
	f.write('<TD ROWSPAN="2" CLASS="tdnames">')
	redblack_string = self.html_redblack(sep="<BR>")
	name_string = ", ".join(self.names)
	f.write(redblack_string)
	if redblack_string and name_string: f.write('<BR>')
	f.write(name_string)
	f.write('&nbsp;</TD></TR>')

	# Flaggdagar
	f.write('<TR><TD CLASS="tdflag">')
	if self.flag_day:
	    f.write('<IMG SRC="flag.gif" ALT="Flaggdag" TITLE="Flaggdag">')
	if self.moonphase is not None:
	    f.write('<IMG SRC="moonphase%d.gif" ALT="%s" TITLE="%s">' % (self.moonphase, self.moonphase_name(), self.moonphase_name()))
	f.write('</TD></TR>')

        if high:
            f.write('<TR><TD CLASS="tdspacer">&nbsp;</TD></TR>')
            

	f.write('</TABLE>')
	f.write('</TD>')

    # Dagblocksliknande
    def html_day(self, f):
	if self.red:
	    colour = "red"
	else:
	    colour = "black"
	
	f.write('<LINK TYPE="text/css" REL="stylesheet" HREF="day.css">')
	f.write('<DIV CLASS="douter">')

	# M�nad
	f.write('<DIV CLASS="dmonth">%s</DIV>' % month_names[self.m])

	# Dag
	f.write('<DIV CLASS="dday %s">%d</DIV>' % (colour, self.d))

	# Veckodag
	f.write('<DIV CLASS="dwday %s">%s v%d</DIV>' % (colour,
							self.wday_name,
							self.week))
	# Flaggdagar och m�nfaser
	f.write('<DIV CLASS="dflag">')
	if self.flag_day:
	    f.write('<IMG SRC="flag.gif">')
	if self.moonphase is not None:
	    f.write('<IMG SRC="moonphase%d.gif">' % self.moonphase)
	f.write('</DIV>')

	# Dagens namn
	f.write('<DIV CLASS="dnames">')
	redblack_string = self.html_redblack(sep="<BR>")
	name_string = ", ".join(self.names)
	f.write(redblack_string)
	if redblack_string and name_string: f.write('<BR>')
	f.write(name_string)
	f.write('&nbsp;</DIV>')

	f.write('</DIV>')


    def dump(self):
	"""Show in text format for debugging."""
	print "%s %4d-%02d-%1d %s%s <%s> <%s>" % (self.jd.GetString_YYYY_MM_DD(),
						  self.wyear, self.week, self.wday,
						  " R"[self.red],
						  " F"[self.flag_day],
						  ",".join(map(str,self.day_names)),
						  ",".join(self.names),
						  )

class YearCal:
    """Class to represent a whole year."""

    def __init__(self, year):
	self.year = year       # �r (exv. 2004)
	self.jd_jan1 = JD(year, 1, 1)
	self.jd_dec31 = JD(year, 12, 31)

	# Skapa alla dagar f�r �ret
	self.days = []
        jd_today = jddate.FromToday()
	jd = self.jd_jan1
	while jd <= self.jd_dec31:
	    self.days.append(DayCal(jd, mark_as_today = (jd==jd_today)))
	    jd = jd + 1

	# Skott�r?
	if len(self.days) == 365 or len(self.days) == 354:
	    self.leap_year = False
	elif len(self.days) == 366 or len(self.days) == 367:
	    self.leap_year = True
	else:
	    assert ValueError, "bad number of days in a year"

	# Helgdagar, flaggdagar med mera
	self.place_names()

	# Namnsdagar
	if year >= 2011:
		self.place_name_day_names("namnsdagar-2011.txt",
				      [(2015,  7, 23, ["Emma","Emmy"]),
				       (2015,  7, 26, ["Jesper","Jasmin"]),
				       (2018,  3,  8, ["Siv","Saga"]),
				       (2018,  9, 14, ["Ida","Ronja"])])
	elif year >= 2001:
	    self.place_name_day_names("namnsdagar-2001.txt")
	elif year >= 1993:
	    self.place_name_day_names("namnsdagar-1993.txt")
	elif year >= 1986:
	    self.place_name_day_names("namnsdagar-1986.txt")
	elif year >= 1901:
	    self.place_name_day_names("namnsdagar-1901.txt",
				      [(1905, 11,  4, ["Sverker"]),
				       (1907, 11, 27, ["Astrid"]),
				       (1953,  3, 25 ,["Marie Beb�delsedag"]),
				       (1953,  6, 24 ,["Johannes D�parens dag"]),
				       (1934, 10, 20, ["Sibylla"])])

	# M�nfaser
	self.place_moonphases()

    # H�mta dag givet m, d
    def get_md(self, m, d):
	jd = JD(self.year, m, d)
	return self.days[jd - self.jd_jan1]

    # H�mta dag givet jd
    def get_jd(self, jd):
	(y, m, d) = jd.GetYMD()
	assert y == self.year
	return self.days[jd - self.jd_jan1]

    # L�gg till information f�r m, d
    def add_info_md(self, m, d, dayclass, flag, name):
	dc = self.get_md(m, d)
	dc.add_info(dayclass, flag, name)

    # L�gg till information f�r jd
    def add_info_jd(self, jd, dayclass, flag, name):
	dc = self.get_jd(jd)
	dc.add_info(dayclass, flag, name)

    # Generator f�r �rets alla dagar
    def generate(self):
	for dc in self.days:
	    yield dc

    # Placera namn
    def place_names(self):
	"""Place holidays etc. in the calendar."""

	# Fasta helgdagar och flaggdagar

	for (from_year, to_year, m, d, dayclass, flag, name) in \
		[
	    # Fasta helgdagar
	    (None, None,  1,  1, MRED , True,  "Ny�rsdagen"),
	    (None, None,  1,  6, MRED,  False, "Trettondedag jul"),
	    (None, None,  5,  1, MRED,  True,  "F�rsta maj"),
	    (None, None, 12, 25, MRED,  True,  "Juldagen"),
	    (None, None, 12, 26, MRED,  False, "Annandag jul"),
	    
	    # Fasta helgdagsaftnar
	    (None, None,  1,  5, MBLACK, False, "Trettondedagsafton"),
	    (None, None,  4, 30, MBLACK, False, "Valborgsm�ssoafton"),
	    (None, None, 12, 24, MBLACK, False, "Julafton"),
	    (None, None, 12, 31, MBLACK, False, "Ny�rsafton"),
	    
	    # Dagar som vissa �r varit "namnsdagar", andra inte
	    (1993, 2000,  2,  2, BLACK, False, "Kyndelsm�ssodagen"),  # Saknas som namnsdag dessa �r
	    (1993, 2000,  3, 25, BLACK, False, "Marie Beb�delsedag"), # Saknas som namnsdag dessa �r
	    (1993, 2000, 11,  1, BLACK, False, "Allhelgonadagen"),    # Saknas som namnsdag dessa �r
	    
	    # Svenska flaggans dag och nationaldagen
	    (1916, 1982,  6,  6, MBLACK, True,  "Svenska flaggans dag"),
	    (1983, 2004,  6,  6, MBLACK, True,  "Sveriges nationaldag"),
	    (2005, None,  6,  6, MRED,   True,   "Sveriges nationaldag"),
	    
	    # Andra flaggdagar
	    (1983, None, 10, 24, BLACK, True,  "FN-dagen"), # Inf�rdes i SFS1982:270
	    (None, None, 11,  6, BLACK, True,  None), # Gustav Adolfsdagen
	    (None, None, 12, 10, BLACK, True,  "Nobeldagen"),
	    (2018, None,  5, 29, BLACK, True, "Veterandagen"),
	    (2018, 2018,  12, 17, BLACK, True, "Minnesdag f�r demokratins genombrott"), # Tillf�llig flaggdag 2018, enligt 2017/18:KU28

	    # Flaggdagar f�r regerande kungahuset
	    
	    # Victoria Ingrid Alice D�sir�e, kronprinsessa
	    # f�dd 1977-07-14
	    # FIXME: Hon l�r inte ha varit kronprinsessa innan successionsordningen
	    # �ndrades, v�l? SFS 1979:935
	    (1980, None,  7, 14, BLACK, True,  None), # f�delsedag
	    (1980, None,  3, 12, BLACK, True,  None), # namnsdag "Viktoria"

	    # Silvia Renate Sommerlath
	    # f�dd 1943-12-23, drottning 1976-06-19
	    (1976, None, 12, 23, BLACK, True,  None), # f�delsedag
	    (1976, None,  8,  8, BLACK, True,  None), # namnsdag "Silvia"
	    
	    # Carl XVI Gustaf Folke Hubertus
	    # f�dd 1946-04-30, kronprins 1950-10-29, kung 1973-09-15
	    (1951, None,  4, 30, BLACK, True,  None), # f�delsedag
	    (1951, None,  1, 28, BLACK, True,  None), # namnsdag "Karl"
	    
	    # Louise Alexandra Maria Ir�ne
	    # f�dd 1889-07-13, gift 1923-11-03, drottning 1950-10-29, d�d 1965-03-07
	    # FIXME: F�rsta almanackan med flaggdagar utsatta 1939, s�tter
	    # det som start. Flaggdag som kronprinsessa innan hon blev drottning.
	    (1939, 1964,  7, 13, BLACK, True,  None), # f�delsedag
	    (1939, 1964,  8, 25, BLACK, True,  None), # namnsdag "Lovisa"

	    # Oscar Fredrik Wilhelm Olaf Gustav VI Adolf
	    # f�dd 1882-11-11, kung 1950-10-29, d�d 1973-09-15
	    # FIXME: F�rsta almanackan med flaggdagar utsatta 1939, s�tter
	    # det som start. Flaggdag som kronprins innan han blev kung.
	    (1939, 1972, 11, 11, BLACK, True,  None), # f�delsedag
	    (1939, 1973,  6,  6, BLACK, True,  None), # namnsdag "Gustav"
	    
	    # Oscar Gustaf V Adolf
	    # f�dd 1858-06-16, kung 1907-12-08, d�d 1950-10-29
	    # FIXME: F�rsta almanackan med flaggdagar utsatta 1939, s�tter
	    # det som start. Flaggdag som kronprins innan han blev kung?
	    (1939, 1950,  6, 16, BLACK, True,  None), # f�delsedag
	    (1939, 1950,  6,  6, BLACK, True,  None), # namnsdag "Gustav"
	    
	     ]:
	    if from_year is not None and self.year < from_year: continue
	    if to_year is not None and self.year > to_year: continue
	    self.add_info_md(m, d, dayclass, flag, name)

	# Dag f�r val till riksdagen �r flaggdag (3 s�ndagen i september)
	# fr�n och med �r 1985.
	# Vart tredje �r -1994
	if 1985 <= self.year <= 1991 and self.year % 3 == 2:
	    vd = first_sunday(self.year, 9, 15)
	    self.add_info_jd(vd, BLACK, True, None)
	# Vart fj�rde �r 1994-
	elif 1994 <= self.year and self.year % 4 == 2:
	    vd = first_sunday(self.year, 9, 15)
	    self.add_info_jd(vd, BLACK, True, None)

	# Skottdagen inf�ll den 24/2 -1996, infaller den 29/2 2000-
	if self.leap_year:
	    if self.year >= 2000:
		self.add_info_md(2, 29, BLACK, False, "Skottdagen")
	    else:
		self.add_info_md(2, 24, BLACK, False, "Skottdagen")
            if self.year == 1712:
                self.add_info_md(2, 30, BLACK, False, "Till�kad")

	# P�sks�ndagen ligger till grund f�r de flesta kyrkliga helgdagarna
	# under �ret, s� den beh�ver vi r�kna ut redan h�r
	pd = easter_sunday(self.year)

	# S�ndagen efter ny�r
	sen = first_sunday(self.year, 1, 2) # F�rsta s�ndagen 2/1-
	if sen < JD(self.year, 1 ,6):  # Sl�s ut av 13dagen och 1 e 13dagen
	    self.add_info_jd(sen, MRED, False, "S�ndagen e ny�r")

	# Kyndelsm�ssodagen (Jungfru Marie Kyrkog�ngsdag)
	jmk = first_sunday(self.year, 2, 2)
	if jmk == pd - 49:
	    # Kyndelsm�ssodagen p� fastlagss�ndagen => Kyndelsm�ssodagen flyttas -1v
	    jmk = jmk -7
	# V�nta med att l�gga dit namnet...

	# S�ndagar efter Trettondedagen
	set = first_sunday(self.year, 1, 7)
	for i in range(1,7):
	    # Sl�s ut av Kyndelsm�ssodagen (efter 1983) och allt p�skaktigt
	    if (set != jmk or self.year <= 1983) and set < pd-63:
		self.add_info_jd(set, RED, False, "%d e trettondedagen" % i)
	    set = set + 7

	# Jungfru Marie Beb�delsedag
	if self.year < 1953:
	    # F�re reformen 25 mars
	    jmb = JD(self.year, 3, 25)
	else:
	    # Efter reformen den n�rmaste s�ndagen (vilket �r 22-28 mars)
	    jmb = first_sunday(self.year, 3, 22)

	# Men: om Jungfru Marie Beb�delsedag hamnar p� p�skdagen eller
	# palms�ndagen, s� flyttas den till s�ndagen innan
	# palms�ndagen (5 i fastan).
	if jmb >= pd - 7 and jmb <= pd:
	    jmb = pd - 14
	# V�nta med att l�gga dit namnet...

	# Fasta, P�sk, Kristi Himmelsf�rd, Pingst

	# Dessa dagar sl�s ut av Kyndelsm�ssodagen
	# fast bara efter 1983
	# Tidigare s� st�r b�da namnen!
	for (jd, name) in [(pd-63, "Septuagesima"),
			   (pd-56, "Sexagesima")]:
	    if jd != jmk or self.year <= 1983:
		self.add_info_jd(jd, RED, False, name)

	# L�gg s� dit Kyndelsm�ssodagen
	if self.year < 1924:
	    self.add_info_jd(jmk, RED, False, "Kyndelsm�ssos�ndagen")
	elif self.year < 1943:
	    self.add_info_jd(jmk, RED, False, "Marie kyrkog�ngsdag eller Kyndelsm�ssodagen")
	else:
	    self.add_info_jd(jmk, RED, False, "Jungfru Marie Kyrkog�ngsdag eller Kyndelsm�ssodagen")

	# Fastlagss�ndagen och icke-helgdagar efter den
	self.add_info_jd(pd-49, RED, False, "Fastlagss�ndagen")
	self.add_info_jd(pd-47, BLACK,False, "Fettisdagen")
	self.add_info_jd(pd-46, BLACK,False, "Askonsdagen")

	# Dessa dagar sl�s ut av Jungfru Marie beb�delsedag,
	# fast bara efter 1983
	# 1952-1983 s� st�r b�da namnen!

	for (jd, name) in [(pd-42, "1 i fastan"),
			   (pd-35, "2 i fastan"),
			   (pd-28, "3 i fastan"),
			   (pd-21, "Midfastos�ndagen"),
			   (pd-14, "5 i fastan")]:
	    if jd != jmb or self.year <= 1983:
		self.add_info_jd(jd, RED, False, name)

	# L�gg s� dit Jungfru Marie beb�delsedag
	self.add_info_jd(jmb, RED, False, "Jungfru Marie beb�delsedag")

	self.add_info_jd(pd- 7, RED,    False, "Palms�ndagen")
	self.add_info_jd(pd- 4, BLACK,  False, "Dymmelonsdagen")
	self.add_info_jd(pd- 3, MBLACK, False, "Sk�rtorsdagen")
	self.add_info_jd(pd- 2, MRED,   False, "L�ngfredagen")
	self.add_info_jd(pd- 1, MBLACK, False, "P�skafton")
	self.add_info_jd(pd+ 0, MRED,   True,  "P�skdagen")
	self.add_info_jd(pd+ 1, MRED,   False, "Annandag p�sk")
	if self.year < 2004:
	    self.add_info_jd(pd+ 7, RED, False, "1 e p�sk")
	    self.add_info_jd(pd+14, RED, False, "2 e p�sk")
	    self.add_info_jd(pd+21, RED, False, "3 e p�sk")
	    self.add_info_jd(pd+28, RED, False, "4 e p�sk")
	else:
	    self.add_info_jd(pd+ 7, RED, False, "2 i p�sktiden")
	    self.add_info_jd(pd+14, RED, False, "3 i p�sktiden")
	    self.add_info_jd(pd+21, RED, False, "4 i p�sktiden")
	    self.add_info_jd(pd+28, RED, False, "5 i p�sktiden")
	self.add_info_jd(pd+35, RED, False, "B�ns�ndagen")
	self.add_info_jd(pd+39, MRED, False, "Kristi himmelsf�rds dag")
	if self.year < 2004:
	    self.add_info_jd(pd+42, RED, False, "6 e p�sk")
	else:
	    self.add_info_jd(pd+42, RED, False, "S�ndagen f Pingst")
	self.add_info_jd(pd+48, MBLACK, False, "Pingstafton")
	self.add_info_jd(pd+49, MRED, True,  "Pingstdagen")
	if self.year < 2005:
	    self.add_info_jd(pd+50, MRED, False, "Annandag pingst")
	else:
	    self.add_info_jd(pd+50, BLACK,False, "Annandag pingst")
	self.add_info_jd(pd+56, RED,False, "Heliga trefaldighets dag")

	# Vissa dagar ska "sl� ut" vanliga "N efter trefaldighet"
	# H�ll reda p� dem i en lista i den takt de r�knas fram
	se3_stoppers = []

	# Midsommardagen
	if self.year < 1953:
	    # F�re 1953 inf�ll midsommardagen alltid p� 24/6
	    msd = JD(self.year, 6, 24)
	else:
	    # Fr�n och med 1953 r�rlig helgdag, l�rdag 20-26/6
	    msd = first_saturday(self.year, 6, 20)
	self.add_info_jd(msd-1, MBLACK, False, "Midsommarafton")
	if self.year <2004:
	    self.add_info_jd(msd+0, MRED,  True,  "Den helige Johannes D�parens dag eller Midsommardagen")
        else:
	    self.add_info_jd(msd+0, MRED,  True,  "Midsommardagen")
	    self.add_info_jd(msd+1, RED,  False,  "Den helige Johannes D�parens dag")
	    se3_stoppers.append(msd+1)

	# Alla Helgons dag
	if self.year < 1953:
	    # NE: "Genom helgdagsreformen 1772 f�rlades firandet till
	    # f�rsta s�ndagen i november"
	    ahd = first_sunday(self.year, 11, 1)
	    # V�nta med att s�tta ut namnet, som inte ska sl� ut n�gon S�ndag e Tref.
	else:
	    # NE: "�r 1953 flyttades dagen i den svenska almanackan till
	    # den l�rdag som infaller 31 oktober till 6 november.
	    ahd = first_saturday(self.year, 10, 31)
	    # V�nta med att s�tta ut namnet (f�r fallet ovan, egentligen)
	    if self.year > 1983:
		self.add_info_jd(ahd+1, RED, False, "S�ndagen e alla helgons dag")
		se3_stoppers.append(ahd+1)

	# Advent (samt Domss�ndagen och S�ndagen f�re domss�ndagen)
	adv1=first_sunday(self.year, 11, 27 )
	self.add_info_jd(adv1-14, RED,  False, "S�ndagen f domss�ndagen")
	self.add_info_jd(adv1- 7, RED,  False, "Domss�ndagen")
	self.add_info_jd(adv1+ 0, MRED, False, "1 i advent")
	self.add_info_jd(adv1+ 7, MRED, False, "2 i advent")
	self.add_info_jd(adv1+14, MRED, False, "3 i advent")
	self.add_info_jd(adv1+21, MRED, False, "4 i advent")


	# S�ndagen e Jul
	sej=first_sunday(self.year, 12, 27)
	if sej <= self.jd_dec31:
	    self.add_info_jd(sej, RED, False, "S�ndagen e jul")

	# Den helige Mikaels dag, s�ndag i tiden 29/9 till 5/10
	hmd = first_sunday(self.year, 9, 29)
	self.add_info_jd(hmd, RED, False, "Den helige Mikaels dag")
	se3_stoppers.append(hmd)

	# Tacks�gelsedagen, andra s�ndagen i oktober
	tsd = first_sunday(self.year, 10, 8)
	self.add_info_jd(tsd, RED, False, "Tacks�gelsedagen")
	se3_stoppers.append(tsd)

	# S�ndagarna efter Trefaldighet
	se3 = pd+63
	for i in range(1,28):
	    # Ska dagen vara en S e Tr?
	    if se3 >= adv1 - 14:
		# Inte l�nt l�ngre efter S f ds
		break
	    
	    # Har dagen redan ett annat namn som har prioritet?
	    if se3 in se3_stoppers:
		se3 += 7
		continue

	    # S�rskilda namn f�r vissa av dagarna
	    if i == 5:
		name = "Apostladagen"
	    elif i == 7:
		name = "Kristi f�rklarings dag"
	    else:
		name = "%d e trefaldighet" % i
	    
	    self.add_info_jd(se3, RED, False, name)
	    se3 += 7

	# S�tt ut A H D
	self.add_info_jd(ahd, MRED, False, "Alla helgons dag")

    def place_name_day_names(self, filename, patches = None):
	for line in open(filename):
	    (ms, ds, ns) = line.strip().split(None,2)
	    m = int(ms)
	    d = int(ds)
	    # Innan �r 2000, d� skottdagen var 24/2, s� flyttades
	    # namnen till senare dagar i februari
	    if self.leap_year and self.year < 2000 and m == 2 and d >= 24: 
		d = d + 1
	    names = ns.split(",")
	    dc = self.get_md(m, d)
	    dc.set_names(names)
	if patches is not None:
	    for (from_year, m, d, names) in patches:
		if self.year >= from_year:
		    dc = self.get_md(m, d)
		    dc.set_names(names)
		    

    # Placera ut m�nfaserna i almanackan.
    # Algoritm: Meeus, Jean, Astronomical Formulae for Calculators, 2 ed, s 159
    def place_moonphases(self):
	# FIXME:
	# int midcycle,cycle;
	# moon_t phase;
	# int h,m;
	# day_cal *dcal;
	# jd_t jd1jan,jd31dec,jd;

	# Ta reda p� en m�ncykel i mitten av �ret (ungef�r)
	midcycle = int((self.year - 1900) * 12.3685) + 6

	# Arbeta bak�t mot b�rjan av �ret och placera ut m�nfaserna

	cycle = midcycle
	phase = 0 # Nym�ne

	while True:
	    jd = moonphase(cycle, phase)
	    if jd < self.jd_jan1: break
	    
	    dc = self.get_jd(jd)
	    dc.set_moonphase(phase)

	    if phase == 0:
		phase = 3
		cycle = cycle - 1
	    else:
		phase = phase -1 

	# Arbeta fram�t mot slutet av �ret och placera ut m�nfaserna

	cycle = midcycle
	phase = 0 # Nym�ne

	while True:
	    jd = moonphase(cycle, phase)
	    if  jd > self.jd_dec31: break

	    dc = self.get_jd(jd)
	    dc.set_moonphase(phase)

	    if phase == 3:
		phase = 0
		cycle = cycle + 1
	    else:
		phase = phase + 1 

    def dump(self):
	"""Show in text format for debugging."""

	for dc in self.generate():
	    dc.dump()

    def month_cal(self, month):
        return MonthCal(self, month)
	
class MonthCal:
    """Class to represent a month of a year."""

    def __init__(self, yearcal, month):
	self.yc = yearcal
	assert 1<= month <= 12
	self.month = month
	self.month_name = month_names[self.month]

	self.num_days = [None, 31, 28, 31, 30, 31, 30,
			 31, 31, 30, 31, 30, 31][self.month]
	if self.yc.leap_year and self.month == 2:
	     self.num_days = 29
             
        if self.yc.year == 1753 and self.month == 2:
             self.num_days = 17

        if self.yc.year == 1712 and self.month == 2:
             self.num_days = 30

                 

    def generate(self):
	for d in range(1,self.num_days+1):
	    dc = self.yc.get_md(self.month, d)
	    yield dc

    def title(self):
        return '%s %s' % (self.month_name, self.yc.year)

    def html_vertical(self, f, for_printing = False):
	# Tabellen med dagarna
	f.write('<TABLE CLASS="vtable">')
	for dc in self.generate():
	    dc.html_vertical(f, for_printing = for_printing)
	f.write('<TR CLASS="v"><TD CLASS="vlast" COLSPAN="5">&nbsp;</TD></TR>')
	f.write('</TABLE>')

    def html_tabular_high(self, f, for_printing = False):
        self.html_tabular(f, for_printing = for_printing, high = True)

    def html_tabular(self, f, for_printing = False, high = False):
	# Tabellen
	f.write('<TABLE CLASS="ttable">')

	# Rubrikrad med veckodagarna
	f.write('<TR CLASS="twd">')
	if self.yc.year >= 1973:
	    days = wday_names[1:]
	else:
	    days = wday_names[7:] + wday_names[1:7]
	f.write('<TD CLASS="twno_empty">&nbsp;</TD>')
	for day in days:
	    f.write('<TD CLASS="twday">%s</TD>' % day)
	f.write('</TR>')
	
	for dc in self.generate():
	    # B�rja ny rad p� f�rsta dagen i m�naden eller veckan
	    if dc.d == 1 or dc.wpos == 1:
		f.write('<TR CLASS="tw">')
		# Veckonummer relevant fr o m 1973
		if dc.y >= 1973:
		    wtext = '<A CLASS="hidelink" HREF="?year=%d&week=%d&type=week">%d</A>' % (dc.wyear,
                                                                                              dc.week,
                                                                                              dc.week)
		else:
		    wtext = "&nbsp;"
		f.write('<TD CLASS="twno">%s</TD>' %wtext)

	    # Fyll ut med tomdagar om det beh�vs i b�rjan
	    if dc.d == 1:
		for i in range(1, dc.wpos):
		    f.write('<TD CLASS="tday_empty">&nbsp;</TD>')

	    # Sj�lva dagen
	    dc.html_tabular(f, for_printing = for_printing, high = high)

	    # Fyll ut med tomdagar om det beh�vs p� slutet
	    if dc.d == self.num_days:
		for i in range(dc.wpos, 7):
		    f.write('<TD CLASS="tday_empty">&nbsp;</TD>')

	    # Avsluta sist i veckan och m�naden
	    if dc.d == self.num_days or dc.wpos == 7:
		f.write('</TR>')

	f.write('</TABLE>')

class WeekCal:
    """Class to represent a week."""

    def __init__(self, week_year, week_no):
	assert 1<= week_no <= 53
        self.week_year = week_year
        self.week_no = week_no
        self.year_cals = {} # We may need more than one year!
        self.days = []

        for wd in range(1, 7+1):
            jd = jddate.FromYWD(self.week_year, self.week_no, wd)
            y, m, d = jd.GetYMD()
            if not y in self.year_cals:
                self.year_cals[y] = YearCal(y)
            self.days.append(self.year_cals[y].get_md(m, d))

    def title(self):
        return 'Vecka %d, %s' % (self.week_no, self.week_year)

    def html_vertical(self, f, for_printing = False):
	# Tabellen med dagarna
	f.write('<TABLE CLASS="vtable">')
	for dc in self.days:
	    dc.html_vertical(f, in_week_cal = True, for_printing = for_printing)
	f.write('<TR CLASS="v"><TD CLASS="vlast" COLSPAN="6">&nbsp;</TD></TR>')
	f.write('</TABLE>')



#
# Invocation
#

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
	year = int(sys.argv[1])
	yc = YearCal(year)
	yc.dump()
    else:
	for year in range(1901,2006):
	    yc = YearCal(year)
	    yc.dump()
