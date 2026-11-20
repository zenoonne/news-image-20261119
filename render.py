#!/usr/bin/env python3
"""Render the make.fun v2 entry: an illustrated newspaper front page summing
up Thursday 19 November 2026.

Layout (1024x1024, drawn entirely offline with Pillow):
  * masthead carrying the date "THURSDAY 19 NOVEMBER 2026"
  * 12 illustrated FEATURE stories (coloured region tag, bold headline,
    one-line subline, code-drawn infographic icon)
  * a dotted world map panel with numbered pins for the features
  * a compact numbered list of the remaining 8 stories
  * a footer crediting the day and the source outlets

Everything is embedded below: no network, no external assets, deterministic.
Running this writes entry.png next to it.

    python3 render.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

W = H = 1024

# ---------------------------------------------------------------- palette ---
BG = (246, 243, 235)      # newsprint cream
INK = (26, 23, 18)
MUTED = (104, 99, 89)
ACCENT = (161, 20, 32)    # masthead red
HAIR = (222, 215, 203)    # hairlines
SEA = (219, 232, 240)
LANDC = (150, 160, 158)
PANEL = (255, 255, 255)
CARDBD = (226, 219, 206)

REGION_COLOR = {
    "Asia": (176, 58, 30),
    "Europe": (28, 88, 160),
    "North America": (24, 128, 84),
    "South America": (150, 96, 22),
    "Africa": (128, 52, 148),
    "Middle East": (186, 120, 16),
    "Oceania": (20, 128, 150),
    "Global": (84, 84, 84),
}

# ------------------------------------------------------------ world map -----
# Simplified world land polygons (lon, lat); public-domain Natural Earth data
# via world-atlas land-110m, simplified for a compact offline map. Carried
# over from v1.
LAND = [
[(-59.6,-80.0),(-60.2,-81.0),(-66.3,-80.3),(-59.6,-80.0)],
[(-45.2,-78.0),(-43.3,-80.0),(-54.2,-80.6),(-48.7,-78.0),(-45.2,-78.0)],
[(-68.5,-71.0),(-71.1,-72.5),(-75.0,-71.7),(-72.1,-71.2),(-70.3,-68.9),(-68.5,-71.0)],
[(-180.0,-84.7),(-170.0,-83.9),(-158.1,-85.4),(-143.1,-85.0),(-153.6,-83.7),(-152.9,-82.0),(-156.8,-81.1),(-146.4,-80.3),(-155.3,-79.1),(-158.4,-76.9),(-151.3,-77.4),(-144.9,-75.2),(-113.9,-73.7),(-107.6,-75.2),(-100.1,-74.9),(-103.7,-72.6),(-76.2,-74.0),(-68.9,-73.0),(-67.1,-72.0),(-68.5,-69.7),(-67.3,-66.9),(-57.8,-63.3),(-65.7,-68.0),(-61.8,-70.7),(-60.8,-73.7),(-70.6,-76.6),(-77.2,-76.7),(-73.7,-77.9),(-78.0,-79.2),(-58.2,-83.2),(-28.6,-80.3),(-29.7,-79.3),(-35.6,-79.5),(-35.8,-78.3),(-17.5,-75.1),(-15.4,-73.1),(-6.9,-70.9),(27.1,-70.5),(33.9,-68.5),(38.6,-69.8),(54.5,-65.8),(61.4,-68.0),(68.9,-67.9),(69.7,-69.2),(67.8,-70.3),(69.1,-70.7),(67.9,-71.9),(69.9,-72.3),(73.9,-69.9),(88.0,-66.2),(95.8,-67.4),(102.8,-65.6),(106.2,-66.9),(113.6,-65.9),(119.8,-67.3),(135.1,-65.3),(137.5,-67.0),(145.5,-66.9),(171.2,-71.7),(163.6,-76.2),(167.0,-78.8),(161.8,-79.2),(159.8,-80.9),(169.4,-83.8),(178.3,-84.5),(-180.0,-84.7)],
[(-67.8,-53.8),(-65.1,-54.7),(-69.2,-55.5),(-74.7,-52.8),(-71.1,-54.1),(-69.3,-52.5),(-67.8,-53.8)],
[(145.4,-40.8),(148.3,-40.9),(147.9,-43.2),(146.0,-43.5),(145.4,-40.8)],
[(173.0,-40.9),(174.2,-41.3),(173.1,-43.9),(169.3,-46.6),(166.7,-46.2),(173.0,-40.9)],
[(174.6,-36.2),(178.5,-37.7),(175.2,-41.7),(173.8,-39.5),(174.7,-37.4),(172.6,-34.5),(174.6,-36.2)],
[(50.1,-13.6),(47.1,-24.9),(44.0,-25.0),(43.3,-22.1),(44.4,-16.2),(47.7,-14.6),(49.2,-12.0),(50.1,-13.6)],
[(143.6,-13.8),(145.4,-15.0),(146.4,-19.0),(153.1,-26.1),(153.1,-30.9),(150.0,-37.4),(146.3,-39.0),(140.6,-38.0),(138.2,-34.4),(136.8,-35.3),(137.8,-32.9),(136.0,-34.9),(131.3,-31.5),(118.0,-35.1),(115.0,-34.2),(115.7,-31.6),(113.3,-26.1),(114.2,-26.3),(114.1,-21.8),(120.9,-19.7),(125.7,-14.2),(129.6,-15.0),(132.4,-11.1),(136.5,-11.9),(135.5,-15.0),(140.2,-17.7),(142.5,-10.7),(143.6,-13.8)],
[(108.6,-6.8),(115.7,-8.4),(105.4,-6.9),(106.1,-5.9),(108.6,-6.8)],
[(134.1,-1.2),(135.5,-3.4),(138.3,-1.7),(144.6,-3.9),(150.7,-10.6),(144.7,-7.6),(142.6,-9.3),(137.6,-8.4),(138.7,-7.3),(137.9,-5.4),(133.0,-4.1),(132.0,-2.8),(133.7,-2.2),(130.5,-0.9),(134.1,-1.2)],
[(125.2,1.4),(120.2,0.2),(120.9,-1.4),(123.3,-0.6),(121.5,-1.9),(123.2,-5.3),(121.0,-2.6),(120.4,-5.5),(119.4,-5.4),(120.0,0.6),(125.2,1.4)],
[(105.8,-5.9),(102.6,-4.2),(95.3,5.5),(97.5,5.2),(103.8,0.1),(106.1,-3.1),(105.8,-5.9)],
[(117.9,1.8),(119.0,0.9),(117.8,0.8),(116.1,-4.0),(110.2,-2.9),(109.1,-0.5),(109.7,2.0),(113.0,3.1),(116.7,6.9),(119.2,5.4),(117.3,3.2),(117.9,1.8)],
[(126.4,8.4),(125.4,5.6),(123.6,7.8),(121.9,7.2),(125.4,9.8),(126.4,8.4)],
[(81.2,6.2),(79.9,6.8),(80.1,9.8),(81.8,7.5),(81.2,6.2)],
[(121.3,18.5),(122.5,17.1),(121.7,14.3),(124.0,13.8),(124.1,12.5),(120.1,15.0),(121.3,18.5)],
[(-72.6,19.9),(-68.3,18.6),(-74.5,18.3),(-72.3,18.7),(-72.6,19.9)],
[(-79.7,22.8),(-74.2,20.3),(-77.8,19.9),(-81.8,22.6),(-85.0,21.9),(-79.7,22.8)],
[(141.0,37.1),(140.3,35.1),(135.8,33.5),(135.1,34.6),(131.0,33.9),(132.0,33.1),(130.2,31.4),(129.4,33.3),(132.6,35.4),(135.7,35.5),(141.4,41.4),(141.0,37.1)],
[(143.9,44.2),(145.5,43.3),(140.0,41.6),(142.0,45.6),(143.9,44.2)],
[(-56.1,50.7),(-56.8,49.8),(-53.5,49.2),(-53.1,46.7),(-54.2,47.8),(-59.3,47.6),(-55.4,51.6),(-56.1,50.7)],
[(143.6,50.7),(144.7,49.0),(143.2,49.3),(143.5,46.1),(142.1,46.0),(142.2,54.2),(143.6,50.7)],
[(-6.8,52.3),(-10.0,51.8),(-9.7,53.9),(-6.7,55.2),(-5.7,54.6),(-6.8,52.3)],
[(-3.0,58.6),(-4.1,57.6),(-2.0,57.7),(-3.1,56.0),(1.7,52.7),(1.4,51.3),(-5.2,50.0),(-3.4,51.4),(-5.3,52.0),(-4.6,53.5),(-2.9,54.0),(-6.2,56.8),(-5.0,58.6),(-3.0,58.6)],
[(-85.2,65.7),(-80.1,63.7),(-87.2,63.5),(-85.2,65.7)],
[(-14.5,66.5),(-13.6,65.1),(-18.7,63.5),(-22.8,64.0),(-21.8,64.4),(-24.0,64.9),(-22.2,65.4),(-24.3,65.6),(-14.5,66.5)],
[(-180.0,69.0),(-174.3,66.3),(-169.9,66.0),(-173.0,64.3),(-179.9,65.9),(-180.0,65.0),(180.0,65.0),(177.4,64.6),(179.2,62.3),(170.3,59.9),(163.5,59.9),(162.0,58.2),(163.2,57.6),(162.1,54.9),(156.8,51.0),(155.9,56.8),(164.5,62.6),(160.1,60.5),(159.3,61.8),(156.7,61.4),(154.2,59.8),(155.0,59.1),(142.2,59.0),(135.1,54.7),(139.9,54.2),(141.4,52.2),(138.2,46.3),(127.5,39.8),(129.1,35.1),(126.5,34.4),(126.9,36.9),(124.7,38.1),(125.3,39.6),(121.1,38.9),(121.6,40.9),(118.0,39.2),(118.9,37.4),(122.4,37.5),(119.2,34.9),(121.9,31.7),(121.7,28.2),(115.9,22.8),(110.4,20.3),(108.5,21.7),(105.9,19.8),(109.3,13.4),(109.2,11.7),(105.2,8.6),(100.1,13.4),(99.2,9.2),(103.0,5.5),(104.2,1.3),(101.4,2.8),(98.3,7.8),(97.2,16.9),(94.2,16.0),(94.3,18.2),(91.4,22.8),(87.0,21.5),(80.3,15.9),(79.9,10.4),(77.5,8.0),(73.5,16.0),(72.6,21.4),(70.5,20.9),(66.4,25.4),(57.4,25.7),(56.5,27.1),(54.7,26.5),(51.5,27.9),(50.1,30.1),(48.0,30.0),(51.8,24.0),(54.0,24.1),(56.4,26.4),(56.8,24.2),(59.8,22.3),(55.3,17.2),(43.5,12.6),(42.7,16.8),(34.6,28.1),(34.9,29.5),(33.9,27.6),(32.4,29.9),(37.5,18.6),(42.7,11.7),(44.6,10.4),(51.1,12.0),(51.0,10.6),(47.7,4.2),(39.2,-4.7),(40.8,-14.7),(34.8,-19.8),(35.5,-24.1),(32.6,-25.7),(32.2,-28.8),(28.2,-32.8),(19.6,-34.8),(11.8,-18.1),(13.7,-10.7),(11.9,-5.0),(8.8,-1.1),(9.4,3.7),(5.9,4.3),(4.3,6.3),(-9.0,4.8),(-16.6,12.2),(-17.6,14.7),(-16.1,18.1),(-17.0,21.9),(-5.9,35.8),(-2.2,35.2),(9.5,37.4),(11.1,36.9),(10.3,33.8),(19.1,30.3),(21.5,32.8),(33.8,31.0),(36.2,36.7),(27.6,36.7),(26.2,39.5),(33.5,42.0),(38.3,40.9),(41.7,42.0),(36.7,45.2),(39.1,47.3),(35.0,46.3),(36.3,45.1),(33.9,44.4),(32.5,45.3),(33.3,46.1),(30.7,46.6),(27.7,42.6),(28.8,41.1),(22.6,40.3),(24.0,37.7),(22.5,36.4),(19.5,41.7),(13.1,45.7),(12.6,44.1),(18.5,40.2),(16.9,40.4),(16.1,38.0),(15.4,40.0),(8.9,44.4),(3.1,43.1),(-2.1,36.7),(-8.9,36.9),(-9.4,43.0),(-1.4,44.0),(-1.2,46.0),(-4.6,48.7),(-1.6,48.6),(-1.9,49.8),(8.1,53.5),(8.5,57.1),(10.6,57.7),(9.6,55.5),(10.9,54.0),(19.7,54.4),(21.3,55.2),(21.6,57.4),(24.1,57.7),(24.3,59.5),(28.0,59.5),(30.2,60.0),(28.6,63.4),(30.0,65.5),(41.1,66.6),(44.5,68.0),(46.6,66.6),(52.4,68.0),(60.0,69.5),(68.9,68.3),(72.4,66.7),(75.0,67.6),(71.4,69.7),(73.0,71.8),(76.9,72.7),(80.7,72.9),(104.5,77.8),(114.3,73.7),(131.0,72.6),(139.9,71.5),(147.7,72.4),(152.5,70.0),(141.0,68.1),(162.7,69.6),(179.9,68.9),(180.0,69.0)],
[(49.1,41.3),(50.4,40.3),(49.2,37.6),(53.8,37.0),(52.7,40.0),(54.7,41.0),(53.7,42.1),(52.8,41.1),(50.3,44.6),(53.0,45.3),(53.0,46.9),(46.7,44.6),(49.1,41.3)],
[(-90.5,69.5),(-87.3,67.2),(-85.5,69.9),(-82.6,69.7),(-81.3,67.6),(-85.8,66.6),(-93.2,62.0),(-94.7,58.9),(-92.3,57.1),(-82.3,55.1),(-79.9,51.2),(-78.6,52.6),(-79.8,54.7),(-76.5,56.5),(-78.5,58.8),(-77.3,59.9),(-78.1,62.3),(-73.8,62.4),(-69.6,61.1),(-69.3,59.0),(-67.7,58.2),(-64.6,60.3),(-61.8,56.3),(-57.3,54.6),(-55.7,52.1),(-60.0,50.2),(-66.4,50.2),(-71.1,46.8),(-65.1,49.2),(-64.5,46.2),(-61.5,45.9),(-60.5,47.0),(-59.8,45.9),(-65.4,43.5),(-66.2,44.5),(-64.4,45.3),(-67.1,45.1),(-70.7,43.0),(-70.0,41.6),(-75.5,39.5),(-75.9,37.2),(-76.4,39.1),(-75.7,35.6),(-81.3,31.4),(-80.4,25.2),(-84.1,30.1),(-93.8,29.7),(-96.6,28.3),(-97.9,22.4),(-96.3,19.3),(-92.0,18.7),(-90.3,21.0),(-87.1,21.5),(-88.9,15.9),(-83.4,15.3),(-83.8,11.1),(-81.4,8.8),(-76.8,8.6),(-71.8,12.4),(-71.7,9.1),(-69.9,12.2),(-68.2,10.6),(-61.9,10.7),(-62.4,9.9),(-57.1,6.0),(-51.3,4.2),(-50.4,-0.1),(-44.9,-1.6),(-44.6,-2.7),(-40.0,-2.9),(-35.6,-5.1),(-34.7,-7.3),(-38.7,-13.1),(-40.9,-21.9),(-47.6,-24.9),(-48.9,-28.7),(-53.8,-34.4),(-58.4,-33.9),(-56.8,-36.9),(-59.2,-38.7),(-62.3,-38.8),(-62.7,-41.0),(-65.1,-41.1),(-63.5,-42.6),(-67.3,-45.6),(-66.0,-48.1),(-69.1,-50.7),(-68.2,-52.4),(-71.0,-53.8),(-74.9,-52.3),(-75.6,-48.7),(-74.1,-46.9),(-75.6,-46.6),(-72.7,-42.4),(-74.3,-43.2),(-71.4,-32.4),(-70.2,-19.8),(-71.5,-17.4),(-76.0,-14.6),(-81.3,-6.1),(-79.8,-2.7),(-80.9,-1.1),(-77.1,3.8),(-78.2,8.3),(-79.6,8.9),(-80.9,7.2),(-85.7,9.9),(-87.5,13.3),(-103.5,18.3),(-105.5,19.9),(-106.0,22.8),(-114.8,31.8),(-109.4,23.2),(-112.2,24.7),(-117.3,33.0),(-120.6,34.6),(-124.4,40.3),(-124.7,48.2),(-122.6,47.1),(-122.8,49.0),(-127.4,50.8),(-134.1,58.1),(-147.1,60.9),(-151.7,59.2),(-150.6,61.3),(-158.4,56.0),(-164.8,54.4),(-157.0,58.9),(-162.0,58.7),(-166.1,61.5),(-160.8,64.8),(-168.1,65.7),(-161.7,66.1),(-166.8,68.4),(-156.6,71.4),(-136.5,68.9),(-128.1,70.5),(-108.9,67.4),(-106.1,68.8),(-101.5,67.6),(-97.7,68.6),(-96.1,67.3),(-94.2,69.1),(-96.5,70.1),(-95.2,71.9),(-90.5,69.5)],
[(-114.2,73.1),(-108.2,71.7),(-108.4,73.1),(-106.5,73.1),(-101.0,70.0),(-102.4,68.8),(-113.3,68.5),(-117.3,70.0),(-112.4,70.4),(-119.4,71.6),(-114.2,73.1)],
[(-86.6,73.2),(-82.3,73.8),(-80.8,72.1),(-72.2,71.6),(-67.0,69.2),(-68.8,68.7),(-61.9,66.9),(-63.9,65.0),(-68.0,66.3),(-64.7,63.4),(-68.8,63.7),(-66.2,61.9),(-74.8,64.7),(-77.7,64.2),(-77.9,65.3),(-74.0,65.5),(-72.9,67.7),(-79.0,70.2),(-89.9,71.2),(-89.4,73.1),(-85.8,73.8),(-86.6,73.2)],
[(-100.4,73.8),(-97.4,73.8),(-96.7,71.7),(-102.5,72.5),(-100.4,72.7),(-101.5,73.4),(-100.4,73.8)],
[(-93.2,72.8),(-95.4,72.1),(-96.0,73.4),(-90.5,73.9),(-93.2,72.8)],
[(-120.5,71.4),(-125.9,71.9),(-123.9,73.7),(-124.9,74.3),(-115.5,73.5),(-120.5,71.4)],
[(-98.5,76.7),(-98.2,75.0),(-102.5,75.6),(-98.5,76.7)],
[(-108.2,76.2),(-105.7,75.5),(-112.2,74.4),(-117.7,75.2),(-115.4,76.5),(-108.2,76.2)],
[(57.5,70.7),(51.5,72.0),(55.6,75.1),(68.9,76.5),(58.5,74.3),(55.4,72.4),(57.5,70.7)],
[(-94.7,77.1),(-79.8,74.9),(-89.8,74.5),(-97.1,76.8),(-94.7,77.1)],
[(105.1,78.3),(99.4,77.9),(102.1,79.3),(105.1,78.3)],
[(18.3,79.7),(21.5,79.0),(15.9,76.8),(10.4,79.7),(18.3,79.7)],
[(25.4,80.4),(27.4,80.1),(17.4,80.3),(25.4,80.4)],
[(99.9,78.9),(91.2,80.3),(95.9,81.3),(99.9,78.9)],
[(-87.0,79.7),(-85.8,79.3),(-90.8,78.2),(-96.7,80.2),(-92.4,81.3),(-87.0,79.7)],
[(-68.5,83.1),(-61.9,82.6),(-76.9,79.3),(-75.4,78.5),(-80.6,76.2),(-89.5,76.5),(-88.3,77.9),(-85.0,77.5),(-88.0,78.4),(-85.1,79.3),(-86.9,80.3),(-81.8,80.5),(-91.6,81.9),(-68.5,83.1)],
[(-27.1,83.5),(-20.8,82.7),(-31.9,82.2),(-12.2,81.3),(-20.0,80.2),(-17.7,80.1),(-19.7,78.8),(-18.5,77.0),(-21.7,76.6),(-19.8,76.1),(-20.7,75.2),(-19.4,74.3),(-23.6,73.3),(-22.3,72.2),(-24.8,72.3),(-21.8,70.7),(-25.5,71.4),(-26.4,70.2),(-22.3,70.1),(-39.8,65.5),(-42.8,62.7),(-43.4,60.1),(-48.3,60.9),(-51.6,63.6),(-54.0,67.2),(-50.9,69.9),(-54.7,69.6),(-54.4,70.8),(-51.4,70.6),(-55.8,71.7),(-54.7,72.6),(-58.6,75.5),(-68.5,76.1),(-71.4,77.0),(-66.8,77.4),(-73.3,78.0),(-65.7,79.4),(-68.0,80.1),(-62.6,81.8),(-44.5,81.7),(-46.8,82.6),(-27.1,83.5)],
]

# ---------------------------------------------------------------- stories ---
# 12 illustrated FEATURES, in reading order.  (n, icon, region, tagline,
# headline, subline, lon, lat)
FEATURES = [
    (1, "flags", "Asia", "ASIA \u00b7 DIPLOMACY",
     "Trump, Xi and Putin hold first trilateral",
     "Shenzhen summit on oil, the UN and nuclear risk", 114.1, 22.6),
    (2, "chart", "North America", "US \u00b7 TECH & MARKETS",
     "Anthropic raises over $100bn in record IPO",
     "Shares open 34% up in Nasdaq debut", -74.0, 40.7),
    (3, "scales", "Europe", "EUROPE \u00b7 JUSTICE",
     "ICJ rules Myanmar committed genocide",
     "World Court ruling on the Rohingya", 4.3, 52.1),
    (4, "tower", "Middle East", "M. EAST \u00b7 CONFLICT",
     "Houthi strike hits a tower in Riyadh",
     "Saudi-led coalition repels Gulf barrage", 46.7, 24.7),
    (5, "painting", "North America", "US \u00b7 CULTURE",
     "Van Gogh sells for a record $190.4m",
     "After a row over its Nazi-era history", -73.0, 41.6),
    (6, "gamepad", "Global", "GLOBAL \u00b7 CULTURE",
     "Grand Theft Auto VI finally launches",
     "Worldwide queues after a 13-year wait", -118.2, 34.0),
    (7, "parliament", "North America", "US \u00b7 POLITICS",
     "Democrats seal biggest House win in 50 years",
     "Clark elected House Majority Leader", -77.0, 38.9),
    (8, "euflag", "Europe", "EUROPE \u00b7 ECONOMY",
     "EU proposes a \u20ac45bn loan to Ukraine",
     "To be repaid from Russian reparations", 4.35, 50.85),
    (9, "climate", "Europe", "EUROPE \u00b7 CLIMATE",
     "COP31: fossil fuels cut from draft deal",
     "Outcry at the Antalya climate talks", 30.7, 36.9),
    (10, "cyclone", "Asia", "ASIA \u00b7 DISASTER",
     "Cyclone Akvan hits India's east coast",
     "Hundreds of thousands evacuated", 85.9, 20.3),
    (11, "helicopter", "South America", "S. AMERICA \u00b7 POLITICS",
     "Hegseth lands in Ecuador on drugs tour",
     "Latin America anti-narcotics mission", -78.5, -0.2),
    (12, "servers", "Global", "GLOBAL \u00b7 ENERGY",
     "Data-centre energy 'could double by 2030'",
     "IEA warns of strained power grids", 2.4, 48.9),
]

# Remaining 8 stories as a compact numbered list.  (n, text)
ALSO = [
    (13, "Senate rejects Iran war-powers limit, 51\u201348"),
    (14, "Turkish court bars Istanbul mayor from 2028 race"),
    (15, "Somalia expels the UAE ambassador"),
    (16, "Egypt secures a $2.3bn IMF deal"),
    (17, "Red giant caught eating its neighbour"),
    (18, "Magnitude 5.7 quake jolts Kumamoto"),
    (19, "Australia 'showing recession hallmarks'"),
    (20, "FIFA U-17 World Cup kicks off in Qatar"),
]

# ------------------------------------------------------------------ fonts ---
_font_cache = {}


def F(size, bold=True, serif=False):
    key = (size, bold, serif)
    f = _font_cache.get(key)
    if f is None:
        if serif:
            path = FONT_SERIF_BOLD if bold else FONT_SERIF
        else:
            path = FONT_BOLD if bold else FONT_REG
        f = ImageFont.truetype(path, size)
        _font_cache[key] = f
    return f


def wrap(d, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ctext(d, cx, y, text, fnt, fill):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


# ------------------------------------------------------------- map drawing --
def _poly_bbox(ring):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


_BBOX = [_poly_bbox(r) for r in LAND]


def _inside(px, py, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > py) != (yj > py):
            if px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside


def _on_land(lon, lat):
    for ring, (x0, y0, x1, y1) in zip(LAND, _BBOX):
        if lon < x0 or lon > x1 or lat < y0 or lat > y1:
            continue
        if _inside(lon, lat, ring):
            return True
    return False


LAT0, LAT1 = -52.0, 84.0   # crop the poles so the map fills its panel


def draw_map(d, x0, y0, mw, mh, feats):
    """Dotted equirectangular world map with numbered feature pins."""
    d.rectangle([x0, y0, x0 + mw, y0 + mh], fill=SEA)

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (LAT1 - lat) / (LAT1 - LAT0) * mh)

    # land as a half-tone grid of dots
    step = 6
    rad = 1.7
    for px in range(x0 + 3, x0 + mw - 2, step):
        lon = (px - x0) / mw * 360.0 - 180.0
        for py in range(y0 + 3, y0 + mh - 2, step):
            lat = LAT1 - (py - y0) / mh * (LAT1 - LAT0)
            if _on_land(lon, lat):
                d.ellipse([px - rad, py - rad, px + rad, py + rad], fill=LANDC)

    # faint equator
    ex0, ey0 = proj(-180, 0)
    ex1, _ = proj(180, 0)
    d.line([(ex0, ey0), (ex1, ey0)], fill=(255, 255, 255), width=1)

    # project pins, then fan overlapping neighbours apart
    pos = [list(proj(f[6], f[7])) for f in feats]
    orig = [list(p) for p in pos]
    min_d = 27.0
    for _ in range(60):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx = pos[i][0] - pos[j][0]
                dy = pos[i][1] - pos[j][1]
                dist = math.hypot(dx, dy)
                if dist < min_d:
                    if dist < 0.01:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    push = (min_d - dist) / 2.0
                    ux, uy = dx / dist, dy / dist
                    pos[i][0] += ux * push
                    pos[i][1] += uy * push
                    pos[j][0] -= ux * push
                    pos[j][1] -= uy * push
                    moved = True
        if not moved:
            break

    # keep inside the panel
    for p in pos:
        p[0] = min(max(p[0], x0 + 12), x0 + mw - 12)
        p[1] = min(max(p[1], y0 + 12), y0 + mh - 12)

    r = 10
    for i, f in enumerate(feats):
        ox, oy = orig[i]
        px, py = pos[i]
        if math.hypot(px - ox, py - oy) > 4:
            d.line([(ox, oy), (px, py)], fill=(255, 255, 255), width=2)
            d.line([(ox, oy), (px, py)], fill=MUTED, width=1)
    for i, f in enumerate(feats):
        px, py = pos[i]
        col = REGION_COLOR[f[2]]
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=2)
        nf = F(11, bold=True)
        num = str(f[0])
        d.text((px - d.textlength(num, font=nf) / 2,
                py - nf.size * 0.62), num, font=nf, fill=(255, 255, 255))


# --------------------------------------------------------------- the icons --
def star_pts(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        rr = r_out if k % 2 == 0 else r_in
        a = math.radians(rot + k * 180.0 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def burst_pts(cx, cy, r_out, r_in, n=10, rot=0):
    pts = []
    for k in range(2 * n):
        rr = r_out if k % 2 == 0 else r_in
        a = math.radians(rot + k * 180.0 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    for k in range(0, 13, 2):
        d.rectangle([x, y + h * k / 13.0, x + w, y + h * (k + 1) / 13.0],
                    fill=(178, 34, 52))
    d.rectangle([x, y, x + w * 0.42, y + h * 7 / 13.0], fill=(20, 40, 110))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    d.polygon(star_pts(x + w * 0.24, y + h * 0.3, h * 0.22, h * 0.09),
              fill=(255, 222, 23))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3.0], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3.0, x + w, y + 2 * h / 3.0], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3.0, x + w, y + h], fill=(213, 43, 30))


def flag_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy = x + w / 2.0, y + h / 2.0
    r = min(w, h) * 0.32
    for k in range(12):
        a = math.radians(k * 30.0)
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.polygon(star_pts(sx, sy, min(w, h) * 0.085, min(w, h) * 0.035),
                  fill=(255, 204, 0))


def icon_flags(d, x, y, w, h):
    gap = 6
    fw = (w - 2 * gap) / 3.0
    fh = h * 0.56
    flag_us(d, x, y, fw, fh)
    flag_cn(d, x + fw + gap, y, fw, fh)
    flag_ru(d, x + 2 * (fw + gap), y, fw, fh)
    for i, f in enumerate((flag_us, flag_cn, flag_ru)):
        d.rectangle([x + i * (fw + gap), y, x + i * (fw + gap) + fw, y + fh],
                    outline=INK, width=1)
    # conference table
    ty = y + fh + h * 0.16
    d.ellipse([x + w * 0.12, ty, x + w * 0.88, ty + h * 0.22],
              fill=(196, 168, 120), outline=INK, width=1)


def icon_chart(d, x, y, w, h):
    ax, ay = x + w * 0.12, y + h * 0.12          # plot origin (top-left)
    bx, by = x + w * 0.88, y + h * 0.9           # bottom-right
    d.line([(ax, ay), (ax, by)], fill=INK, width=2)
    d.line([(ax, by), (bx, by)], fill=INK, width=2)
    vals = [0.28, 0.45, 0.62, 0.86]
    bw = (bx - ax) / (len(vals) * 1.6)
    for i, v in enumerate(vals):
        cx = ax + (i + 0.55) * ((bx - ax) / len(vals))
        top = by - (by - ay) * v
        d.rectangle([cx - bw / 2, top, cx + bw / 2, by], fill=(28, 88, 160))
    # ascending arrow
    d.line([(ax + w * 0.06, by - h * 0.1), (bx - w * 0.05, ay + h * 0.05)],
           fill=(24, 128, 84), width=3)
    tipx, tipy = bx - w * 0.05, ay + h * 0.05
    d.polygon([(tipx, tipy), (tipx - 9, tipy + 2), (tipx - 2, tipy + 9)],
              fill=(24, 128, 84))


def icon_scales(d, x, y, w, h):
    cx = x + w / 2.0
    top = y + h * 0.16
    beam = y + h * 0.24
    d.line([(cx, top), (cx, y + h * 0.82)], fill=(70, 70, 70), width=3)
    d.line([(x + w * 0.12, beam), (x + w * 0.88, beam)], fill=(70, 70, 70), width=3)
    d.ellipse([cx - 4, top - 5, cx + 4, top + 3], fill=(70, 70, 70))
    for ex in (x + w * 0.12, x + w * 0.88):
        d.line([(ex, beam), (ex, beam + h * 0.18)], fill=(70, 70, 70), width=2)
        d.polygon([(ex - w * 0.14, beam + h * 0.18),
                   (ex + w * 0.14, beam + h * 0.18),
                   (ex, beam + h * 0.38)], fill=(150, 150, 150),
                  outline=(70, 70, 70))
    d.rectangle([cx - w * 0.16, y + h * 0.82, cx + w * 0.16, y + h * 0.9],
                fill=(70, 70, 70))


def icon_tower(d, x, y, w, h):
    tw, th = w * 0.30, h * 0.72
    tx, ty = x + w * 0.2, y + h * 0.24
    d.rectangle([tx, ty, tx + tw, ty + th], fill=(120, 130, 140),
                outline=INK, width=1)
    for r in range(6):
        for c in range(2):
            wx = tx + tw * (0.18 + c * 0.4)
            wy = ty + th * (0.1 + r * 0.14)
            d.rectangle([wx, wy, wx + tw * 0.2, wy + th * 0.07],
                        fill=(245, 235, 180))
    # explosion
    bx, by = tx + tw * 1.05, ty + th * 0.16
    d.polygon(burst_pts(bx, by, w * 0.18, w * 0.08, n=11),
              fill=(214, 120, 20))
    d.polygon(burst_pts(bx, by, w * 0.11, w * 0.05, n=9, rot=12),
              fill=(200, 46, 32))
    # smoke plume
    for k, rr in enumerate((0.05, 0.07, 0.06)):
        sx = bx + w * 0.1 + k * w * 0.06
        sy = by - h * 0.16 - k * h * 0.1
        d.ellipse([sx - w * rr, sy - w * rr, sx + w * rr, sy + w * rr],
                  fill=(180, 180, 185))


def icon_painting(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(146, 108, 62))
    px0, py0, px1, py1 = x + w * 0.1, y + h * 0.1, x + w * 0.9, y + h * 0.9
    d.rectangle([px0, py0, px1, py1], fill=(240, 236, 220))
    horizon = py0 + (py1 - py0) * 0.52
    d.rectangle([px0, py0, px1, horizon], fill=(150, 196, 224))   # sky
    d.rectangle([px0, horizon, px1, py1], fill=(224, 200, 96))    # field
    d.ellipse([px0 + (px1 - px0) * 0.55, py0 + (py1 - py0) * 0.12,
               px0 + (px1 - px0) * 0.75, py0 + (py1 - py0) * 0.32],
              fill=(250, 220, 90))                                # sun
    # cypress
    cx = px0 + (px1 - px0) * 0.28
    d.polygon([(cx - w * 0.07, py1), (cx + w * 0.07, py1),
               (cx + w * 0.03, horizon - h * 0.1),
               (cx, horizon - h * 0.2),
               (cx - w * 0.03, horizon - h * 0.1)], fill=(70, 110, 60))
    # a sunflower
    fx = px0 + (px1 - px0) * 0.72
    fy = py1 - h * 0.14
    for k in range(8):
        a = math.radians(k * 45)
        d.ellipse([fx + math.cos(a) * 6 - 3, fy + math.sin(a) * 6 - 3,
                   fx + math.cos(a) * 6 + 3, fy + math.sin(a) * 6 + 3],
                  fill=(240, 196, 30))
    d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(110, 76, 30))


def icon_gamepad(d, x, y, w, h):
    body = [x + w * 0.08, y + h * 0.24, x + w * 0.92, y + h * 0.82]
    d.rounded_rectangle(body, radius=int(h * 0.24), fill=(64, 66, 78))
    # grips
    d.ellipse([x + w * 0.04, y + h * 0.5, x + w * 0.3, y + h * 0.94],
              fill=(64, 66, 78))
    d.ellipse([x + w * 0.7, y + h * 0.5, x + w * 0.96, y + h * 0.94],
              fill=(64, 66, 78))
    # d-pad
    pcx, pcy = x + w * 0.32, y + h * 0.56
    d.rectangle([pcx - 3, pcy - 9, pcx + 3, pcy + 9], fill=(220, 220, 226))
    d.rectangle([pcx - 9, pcy - 3, pcx + 9, pcy + 3], fill=(220, 220, 226))
    # buttons
    bcx, bcy = x + w * 0.68, y + h * 0.56
    for dx, dy, col in ((0, -7, (232, 90, 90)), (7, 0, (90, 190, 110)),
                        (0, 7, (90, 150, 232)), (-7, 0, (232, 210, 90))):
        d.ellipse([bcx + dx - 3, bcy + dy - 3, bcx + dx + 3, bcy + dy + 3],
                  fill=col)


def icon_parliament(d, x, y, w, h):
    ccx = x + w / 2.0
    ccy = y + h * 0.94
    rowh = h * 0.2
    nf = 0
    rows = 4
    dots = []
    for r in range(rows):
        rad = (w * 0.46) * (1 - r * 0.2) + 6
        count = 11 - r * 2
        for k in range(count):
            a = math.radians(180 * (k + 0.5) / count)
            px = ccx - math.cos(a) * rad
            py = ccy - math.sin(a) * rad * 0.92
            dots.append((px, py))
    # colour by side: left = majority
    for px, py in dots:
        col = (28, 88, 160) if px < ccx else (186, 60, 60)
        d.ellipse([px - 3.2, py - 3.2, px + 3.2, py + 3.2], fill=col)
    # speaker's seat
    d.rectangle([ccx - w * 0.05, y + h * 0.62, ccx + w * 0.05, y + h * 0.82],
                fill=(70, 70, 70))


def icon_euflag(d, x, y, w, h):
    fw = w * 0.56
    fh = h * 0.5
    fy = y + h * 0.06
    flag_eu(d, x + w * 0.04, fy, fw, fh)
    d.rectangle([x + w * 0.04, fy, x + w * 0.04 + fw, fy + fh],
                outline=INK, width=1)
    # euro coin
    ccx, ccy = x + w * 0.76, y + h * 0.72
    cr = min(w, h) * 0.22
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(232, 190, 60),
              outline=(150, 110, 20), width=2)
    d.arc([ccx - cr * 0.5, ccy - cr * 0.5, ccx + cr * 0.35, ccy + cr * 0.5],
          40, 320, fill=(90, 66, 10), width=2)
    for dy in (-cr * 0.14, cr * 0.14):
        d.line([(ccx - cr * 0.45, ccy + dy), (ccx + cr * 0.25, ccy + dy)],
               fill=(90, 66, 10), width=2)


def icon_climate(d, x, y, w, h):
    cr = min(w, h) * 0.34
    ccx, ccy = x + w * 0.42, y + h * 0.56
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(92, 156, 208),
              outline=(40, 90, 140), width=1)
    for blob in (((-0.3, -0.2, 0.2, 0.15),),):
        pass
    d.ellipse([ccx - cr * 0.7, ccy - cr * 0.7, ccx - cr * 0.1, ccy - cr * 0.1],
              fill=(104, 168, 110))
    d.ellipse([ccx + cr * 0.05, ccy + cr * 0.0, ccx + cr * 0.75, ccy + cr * 0.6],
              fill=(104, 168, 110))
    d.ellipse([ccx - cr * 0.4, ccy + cr * 0.3, ccx + cr * 0.2, ccy + cr * 0.8],
              fill=(104, 168, 110))
    # leaf sprouting
    lx, ly = x + w * 0.8, y + h * 0.3
    d.line([(lx, ly + h * 0.18), (lx, ly)], fill=(60, 120, 60), width=2)
    d.arc([lx - 10, ly - 6, lx + 2, ly + 8], 90, 250, fill=(46, 140, 70),
          width=3)
    d.arc([lx - 2, ly - 6, lx + 10, ly + 8], 290, 90, fill=(46, 140, 70),
          width=3)


def icon_cyclone(d, x, y, w, h):
    cx, cy = x + w / 2.0, y + h / 2.0
    R = min(w, h) * 0.42
    for k in range(3):
        f = 1 - k * 0.32
        a0 = 200 + k * 40
        d.arc([cx - R * f, cy - R * f, cx + R * f, cy + R * f], a0, a0 + 230,
              fill=(30, 110, 150), width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(200, 60, 40))


def icon_helicopter(d, x, y, w, h):
    g = (74, 78, 84)
    # body
    d.ellipse([x + w * 0.24, y + h * 0.42, x + w * 0.66, y + h * 0.72],
              fill=g, outline=INK, width=1)
    # cockpit window
    d.ellipse([x + w * 0.5, y + h * 0.46, x + w * 0.64, y + h * 0.62],
              fill=(180, 214, 234))
    # tail boom + fin
    d.polygon([(x + w * 0.62, y + h * 0.54), (x + w * 0.9, y + h * 0.46),
               (x + w * 0.9, y + h * 0.54), (x + w * 0.62, y + h * 0.62)],
              fill=g)
    d.polygon([(x + w * 0.86, y + h * 0.3), (x + w * 0.94, y + h * 0.48),
               (x + w * 0.86, y + h * 0.5)], fill=g)
    # main rotor
    d.line([(x + w * 0.12, y + h * 0.3), (x + w * 0.8, y + h * 0.3)],
           fill=INK, width=3)
    d.line([(x + w * 0.45, y + h * 0.3), (x + w * 0.45, y + h * 0.42)],
           fill=INK, width=2)
    # tail rotor
    d.line([(x + w * 0.9, y + h * 0.3), (x + w * 0.9, y + h * 0.5)],
           fill=INK, width=2)
    # skids
    d.line([(x + w * 0.28, y + h * 0.72), (x + w * 0.28, y + h * 0.8)],
           fill=INK, width=2)
    d.line([(x + w * 0.6, y + h * 0.72), (x + w * 0.6, y + h * 0.8)],
           fill=INK, width=2)
    d.line([(x + w * 0.2, y + h * 0.82), (x + w * 0.7, y + h * 0.82)],
           fill=INK, width=2)


def icon_servers(d, x, y, w, h):
    sw = w * 0.5
    sx = x + w * 0.08
    sh = h * 0.22
    for r in range(3):
        sy = y + h * 0.1 + r * (sh + h * 0.06)
        d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=3,
                            fill=(56, 60, 70), outline=INK, width=1)
        for c in range(3):
            lx = sx + sw * (0.14 + c * 0.28)
            ly = sy + sh * 0.5
            d.ellipse([lx - 2.5, ly - 2.5, lx + 2.5, ly + 2.5],
                      fill=(90, 220, 120))
    # lightning bolt
    bx, by = x + w * 0.78, y + h * 0.22
    d.polygon([(bx, by), (bx - w * 0.14, by + h * 0.3),
               (bx - w * 0.02, by + h * 0.3), (bx - w * 0.1, by + h * 0.62),
               (bx + w * 0.12, by + h * 0.22), (bx + w * 0.0, by + h * 0.22),
               (bx + w * 0.08, by)], fill=(240, 200, 30),
              outline=(170, 130, 10))


ICONS = {
    "flags": icon_flags,
    "chart": icon_chart,
    "scales": icon_scales,
    "tower": icon_tower,
    "painting": icon_painting,
    "gamepad": icon_gamepad,
    "parliament": icon_parliament,
    "euflag": icon_euflag,
    "climate": icon_climate,
    "cyclone": icon_cyclone,
    "helicopter": icon_helicopter,
    "servers": icon_servers,
}


# --------------------------------------------------------------- the page ---
def fit_headline(d, text, maxw, maxlines):
    for size in range(20, 14, -1):
        f = F(size, bold=True, serif=True)
        lines = wrap(d, text, f, maxw)
        if len(lines) <= maxlines:
            return f, lines
    f = F(15, bold=True, serif=True)
    return f, wrap(d, text, f, maxw)


def fit_sub(d, text, maxw, maxlines):
    for size in range(13, 9, -1):
        f = F(size, bold=False)
        lines = wrap(d, text, f, maxw)
        if len(lines) <= maxlines:
            return f, lines
    f = F(10, bold=False)
    return f, wrap(d, text, f, maxw)


def draw_feature(d, f, cx, cy, cw, ch):
    n, icon, region, tag, headline, sub = f[0], f[1], f[2], f[3], f[4], f[5]
    pad = 7
    iw = 100
    ih = 100
    ix = cx + pad
    iy = cy + (ch - ih) / 2.0
    # icon panel
    d.rounded_rectangle([ix, iy, ix + iw, iy + ih], radius=8, fill=PANEL,
                        outline=CARDBD, width=1)
    ICONS[icon](d, ix + 9, iy + 9, iw - 18, ih - 18)

    tx = ix + iw + 10
    tw = cx + cw - pad - tx
    col = REGION_COLOR[region]

    f_tag = F(10, bold=True)
    fh, hlines = fit_headline(d, headline, tw, 3)
    fs, slines = fit_sub(d, sub, tw, 2)
    lh = int(fh.size * 1.14)
    slh = int(fs.size * 1.28)
    tag_h = 13
    block = tag_h + len(hlines) * lh + 3 + len(slines) * slh
    ty = cy + (ch - block) / 2.0

    d.text((tx, ty), tag, font=f_tag, fill=col)
    # small colour chip before the tag
    d.rectangle([tx - 5, ty + 2, tx - 2, ty + 9], fill=col)
    ty += tag_h
    for ln in hlines:
        d.text((tx, ty), ln, font=fh, fill=INK)
        ty += lh
    ty += 3
    for ln in slines:
        d.text((tx, ty), ln, font=fs, fill=MUTED)
        ty += slh


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    M = 14
    cx = W / 2.0

    # ---------------- masthead ----------------
    d.text((M, 8), "20 STORIES", font=F(12, bold=True), fill=MUTED)
    d.text((M, 24), "THURSDAY'S NEWS", font=F(12, bold=True), fill=MUTED)
    d.text((W - M - d.textlength("ONE PAGE", font=F(12, bold=True)), 8),
           "ONE PAGE", font=F(12, bold=True), fill=MUTED)
    d.text((W - M - d.textlength("ILLUSTRATED", font=F(12, bold=True)), 24),
           "ILLUSTRATED", font=F(12, bold=True), fill=MUTED)

    name = "THE WORLD TODAY"
    fn = F(38, bold=True, serif=True)
    ctext(d, cx, 6, name, fn, INK)

    dt = "THURSDAY 19 NOVEMBER 2026"
    fd = F(34, bold=True)
    ctext(d, cx, 52, dt, fd, ACCENT)

    d.rectangle([M, 96, W - M, 99], fill=INK)
    strap = "The day's most consequential stories, illustrated \u00b7 six continents and the world"
    ctext(d, cx, 103, strap, F(13, bold=False), MUTED)
    d.rectangle([M, 126, W - M, 127], fill=HAIR)

    # ---------------- features ----------------
    fy0 = 136
    fy1 = 688
    cols, rows = 3, 4
    gap = 12
    cellw = (W - 2 * M - (cols - 1) * gap) / 3.0
    cellh = (fy1 - fy0) / rows

    # hairlines between columns / rows
    for c in range(1, cols):
        x = M + c * cellw + (c - 0.5) * gap
        d.line([(x, fy0), (x, fy1)], fill=HAIR, width=1)
    for r in range(1, rows):
        y = fy0 + r * cellh
        d.line([(M, y), (W - M, y)], fill=HAIR, width=1)

    for i, f in enumerate(FEATURES):
        r, c = divmod(i, cols)
        fx = M + c * (cellw + gap)
        fyy = fy0 + r * cellh
        draw_feature(d, f, fx, fyy, cellw, cellh)

    d.rectangle([M, fy1 + 2, W - M, fy1 + 3], fill=INK)

    # ---------------- map panel ----------------
    by0 = fy1 + 9
    by1 = 986
    bpw = 500
    d.rectangle([M, by0, M + bpw, by1], fill=PANEL, outline=INK, width=2)
    d.text((M + 12, by0 + 7), "WHERE IT HAPPENED", font=F(19, bold=True),
           fill=INK)
    note = "numbered pins mark the illustrated stories"
    f_note = F(10, bold=False)
    d.text((M + bpw - 12 - d.textlength(note, font=f_note), by0 + 14),
           note, font=f_note, fill=MUTED)
    mwid = bpw - 26
    mhgt = int(round(mwid * (LAT1 - LAT0) / 360.0))
    mx = M + 13
    my = by0 + 34
    draw_map(d, mx, my, mwid, mhgt, FEATURES)

    # legend, wrapped into up to two rows
    lregions = ["Asia", "Europe", "North America", "South America",
                "Middle East", "Global", "Africa", "Oceania"]
    used = []
    for f in FEATURES:
        if f[2] not in used:
            used.append(f[2])
    f_leg = F(11, bold=True)
    lx = M + 14
    ly = my + mhgt + 9
    maxx = M + bpw - 10
    for reg in [r for r in lregions if r in used]:
        lbl = reg.upper()
        itemw = 14 + d.textlength(lbl, font=f_leg) + 10
        if lx + itemw > maxx:
            lx = M + 14
            ly += 16
        d.ellipse([lx, ly + 1, lx + 9, ly + 10], fill=REGION_COLOR[reg],
                  outline=(200, 195, 185), width=1)
        d.text((lx + 13, ly), lbl, font=f_leg, fill=INK)
        lx += itemw

    # ---------------- also-on-thursday list ----------------
    lx0 = M + bpw + 12
    lw = W - M - lx0
    d.rectangle([lx0, by0, lx0 + lw, by1], fill=PANEL, outline=INK, width=2)
    d.text((lx0 + 12, by0 + 7), "ALSO ON THURSDAY 19 NOVEMBER",
           font=F(15, bold=True), fill=ACCENT)
    d.rectangle([lx0 + 12, by0 + 28, lx0 + lw - 12, by0 + 29], fill=HAIR)
    nf = F(14, bold=True)
    tf = F(13, bold=False)
    ly = by0 + 36
    rowh = (by1 - 12 - ly) / len(ALSO)
    for n, text in ALSO:
        d.text((lx0 + 12, ly + 1), "%d" % n, font=nf, fill=REGION_COLOR[
            "Europe"] if False else ACCENT)
        lines = wrap(d, text, tf, lw - 44)
        ty = ly
        for ln in lines[:2]:
            d.text((lx0 + 38, ty), ln, font=tf, fill=INK)
            ty += 15
        ly += rowh

    # ---------------- footer ----------------
    d.rectangle([M, 990, W - M, 991], fill=INK)
    foot1 = "Every story happened or was first reported on Thursday 19 November 2026."
    ctext(d, cx, 994, foot1, F(12, bold=True), INK)
    foot2 = ("Sources: CNBC, Al Jazeera, NPR, BBC, Euronews, Le Monde, "
             "Africanews, ABC News, The Japan Times, The Times of India, The Hindu, Yahoo Sports.")
    ctext(d, cx, 1009, foot2, F(10, bold=False), MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
