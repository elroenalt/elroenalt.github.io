from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import json
import math
import copy
from pathlib import Path
import pandas as pd

assetsDir = Path(__file__).parent / "assets"

with open(assetsDir / "default.json", "r", encoding="utf-8") as f:
    default_planetPresets = json.load(f)


composition_planet_comp = {1:"gas-Giant",3:"gas-Giant",5:"planet",1000:"earth-like"} #{1:"gas-Giant",3:"ice-Giant",5:"planet",1000:"earth-like"}
sun_to_earth_mass = 332946.0
sun_to_earth_radius = 109.123


def build_planet_list(group):
    planetCount = 0
    planets = []

    for _, row in group.iterrows():
        radius, mass = row.get('pl_rade',1), row.get('pl_bmasse',1)  
        gravity = round(((mass)/(radius**2)), 3)
        density_rel = mass / (radius**3)
        density_gcm3 = round(density_rel*5.514, 3)
        raw_name = row['pl_name']

        if isinstance(raw_name, bytes):
            planet_name = raw_name.decode('utf-8')
        else:
            planet_name = str(raw_name)
        planet_name = planet_name.strip()

        planets.append({
            "name": planet_name,
            "radius": radius,
            "mass": mass,
            "gravity": gravity,
            "density_rel": density_rel,
            "density_gcm3": density_gcm3,
            "orbital_period_days": row.get('pl_orbper',360),
            "temperature": row.get('pl_eqt',273),
            "orbital_distance": row.get('pl_orbsmax',1),
            "discovered_year": row.get('disc_year',"!no Data provided!"),
            "link_website": f"https://exoplanetarchive.ipac.caltech.edu/overview/{planet_name.replace(' ', '%20')}"
        })

    return planets

def get_Star_XYZ(row):
    dec = math.radians(row.get("dec"))
    ra = math.radians(row.get("ra"))
    dist_AU = row.get("dist_AU",1.0)

    return {
        "x": dist_AU * math.cos(dec) * math.cos(ra),
        "y": dist_AU * math.cos(dec) * math.sin(ra) ,
        "z": dist_AU * math.sin(dec)

    }
sun_rad, sun_temp = 1, 5778

def generateGroupSystem(group,name):
    row = group.iloc[0]
    radius, mass, temp = row.get("st_rad",1.0), row.get("st_mass",1.0), row.get("st_teff", 5778.0)
    starMass = mass*sun_to_earth_mass
    starRadius = radius*sun_to_earth_radius
    star_lum = (radius/sun_rad)**2 * (temp/sun_temp)**4
    starGravity = round(((starMass)/(starRadius**2)),3)

    system = {
        "star_system": name,
        "star_properties": {
            "name": name,
            "gravity": starGravity,
            "radius": starRadius,
            "mass": starMass,
            "temperature": row.get('st_teff',5778.0),
            "dist_AU": row.get('dist_AU'),
            "dist_LY": row.get('dist_LY'),
            "luminosity": round(star_lum, 4),
            "pos": get_Star_XYZ(row),
        },
        "planet_count": int(group['sy_pnum'].iloc[0]),
        "planets": build_planet_list(group)
    }

    return system

def get_StarSystems(count,max_dist_ly=10):
    max_dist_pc = max_dist_ly / 3.26156

    raw_data = NasaExoplanetArchive.query_criteria(
        table="pscomppars",
        select="""
            hostname, sy_dist, sy_snum, sy_pnum, st_rad, st_mass, st_teff, st_lum,

            pl_name, pl_rade, pl_bmasse, pl_orbper, pl_eqt, pl_orbsmax, ra, dec, disc_year

        """,
        where = (
            f"sy_dist <= {max_dist_pc} "
            "AND pl_name IS NOT NULL "
            "AND sy_dist IS NOT NULL"
        ),
        order="sy_dist ASC"
    )

    for col in ['hostname', 'pl_name']:
        if col in raw_data.colnames:
            raw_data[col] = [str(val).strip() for val in raw_data[col]]

    df = raw_data.to_pandas()
    sy_dist = df.get('sy_dist', pd.Series(0.0, index=df.index)).fillna(0.0)

    df['dist_AU'] = round(sy_dist * 206265.0, 10)
    df['dist_LY'] = round(sy_dist * 3.26156, 4)


    groups = df.groupby('hostname')
    systems = [generateGroupSystem(group,name) for name, group in groups]

    if(count):
        count = count if count <= len(systems) else len(systems)
        return systems[:count]
    else:
        return systems

def getXYZValuesColor(temp,radiationIntensity):
    if math.isnan(temp) or temp <= 2300:
        temp = 2300

    multi = 1.2 * (radiationIntensity / 2.0)
    min_value = 0
    x = (-3.0258469*(10**9))/(temp**3) + (2.1070379*(10**6))/(temp**2) + (0.2226347*(10**3))/(temp) + 0.240390

    y = 3.0817480*(x**3) - 5.89338670*(x**2) + 3.75112997*(x) - 0.37001483

    Y = 1

    X = max((x*Y)/(y),min_value)

    Z = max(((1-x-y)*Y)/(y),min_value)

    return round(X * multi, 4), round(Y * multi, 4), round(Z * multi, 4)

import re

import unicodedata

def to_valid_resource_location(name: str) -> str:
    normalized = unicodedata.normalize('NFKD', name)
    ascii_str = normalized.encode('ASCII', 'ignore').decode('utf-8')
    lowered = ascii_str.lower().replace(" ", "_")
    validStr = re.sub(r'[^a-z0-9_.-]', '', lowered)
    validStr = re.sub(r'_+', '_', validStr).strip('_')
    return validStr

def getStarTexture(temp):
    if temp < 3700: return {"namespace": "adv_rocketry", "path": "textures/planet/baked_8k_sun_original.png"}
    elif temp < 5200: return {"namespace": "adv_rocketry", "path": "textures/planet/baked_8k_sun_adjusted.png"}
    elif temp < 6000: return {"namespace": "adv_rocketry", "path": "textures/planet/baked_8k_sun_adjusted.png"}
    elif temp < 10000: return {"namespace": "adv_rocketry", "path": "textures/planet/baked_8k_sun_grayscale.png"}
    else: return {"namespace": "adv_rocketry", "path": "textures/planet/baked_8k_sun_grayscale.png"}

def generateStarProperties(systemData):
    star_data = systemData["star_properties"]
    star_properties = copy.deepcopy(default_planetPresets["star"])

    radiationIntensity = max(2 * (star_data["radius"]/sun_to_earth_radius)**2 * (star_data["temperature"]/5778)**4, 0.1)
    star_data["radiationIntensity"] = radiationIntensity

    emissiveTextureTintColor = 20*star_data["luminosity"]
    emissiveLightColor = getXYZValuesColor(star_data["temperature"],radiationIntensity)
    star_properties["radiationIntensity"] = radiationIntensity

    star_properties["emissiveTextureTintColor"] = {
        "x":emissiveTextureTintColor,"y":emissiveTextureTintColor,"z":emissiveTextureTintColor
    }

    star_properties["emissiveLightColor"] = {
        "x":emissiveLightColor[0],"y":emissiveLightColor[1],"z":emissiveLightColor[2]
    }

    star_properties["description"] = f"""
        A system {star_data["dist_LY"]} light years away from sol, with {systemData["planet_count"]} discovered exo-planets.
        The star has a radius of {star_data["radius"]} earths, a mass of  {star_data["mass"]} earths and a temperatur of {star_data["temperature"]} K."""

    star_properties["name"] = star_data["name"]
    star_properties["position"] = star_data["pos"]
    star_properties["gravitationalMultiplier"] = star_data["gravity"]
    star_properties["earthRadiusMultiplier"] = star_data["radius"]
    star_properties["isKnown"] = True
    star_properties["texture"] = getStarTexture(star_data["temperature"])
    star_properties["currentTemp"] = star_data["temperature"]
    star_properties["dimensionId"] = {
        "namespace": "adv_rocketry",
        "path": to_valid_resource_location(star_properties["name"]+"_star")
    }

    return star_properties

def getPlanetProperties(planet_data,star_data):

    planet_density = planet_data["density_gcm3"]
    planet_temp = planet_data["temperature"]
    planet_dist = planet_data["orbital_distance"]
    star_lum = star_data["luminosity"]
    eff_dist = planet_dist / math.sqrt(star_lum)
    ar_in_game_flux = star_data["radiationIntensity"] / (planet_dist ** 2)

    if planet_density < 1:
        type = "gas giant"
        #gas-giant

        if planet_temp < 273:
            planet_properties = copy.deepcopy(default_planetPresets["cold-gas-giant"])
        else:
            planet_properties = copy.deepcopy(default_planetPresets["hot-gas-giant"])

    elif planet_density < 2:
        type = "ice gas giant"
        #ice-gas-giant

        planet_properties = copy.deepcopy(default_planetPresets["ice-gas-giant"])

    elif planet_density < 4:
        type = "ocean planet"
        #ocean planet

        if planet_temp < 273:
            planet_properties = copy.deepcopy(default_planetPresets["ice-planet"])
        else:
            planet_properties = copy.deepcopy(default_planetPresets["ocean-planet"])

    elif planet_density < 6.5:
        type = "terrestrial"
        #terrestrial planet

        print(eff_dist,ar_in_game_flux)
        if ar_in_game_flux > 15.0:
            type += " hot planet"
            planet_properties = copy.deepcopy(default_planetPresets["hot-terrestrial-planet"])
        elif planet_dist < 0.3:
            type += " hot planet"
            planet_properties = copy.deepcopy(default_planetPresets["hot-terrestrial-planet"])

        elif planet_dist > 3:
            type += " cold planet"
            planet_properties = copy.deepcopy(default_planetPresets["cold-terrestrial-planet"])

        elif planet_temp < 273:
            type += " cold planet"
            planet_properties = copy.deepcopy(default_planetPresets["cold-terrestrial-planet"])

        elif planet_temp < 353:
            type += " earthlike planet"
            planet_properties = copy.deepcopy(default_planetPresets["earthlike-terrestrial-planet"])

        elif planet_temp < 1200:
            type += " hot planet"
            planet_properties = copy.deepcopy(default_planetPresets["hot-terrestrial-planet"])

        else:
            type += " volcanic planet"
            planet_properties = copy.deepcopy(default_planetPresets["volcanic-terrestrial-planet"])

    else:
        type = "heavy iron planet"
        #heavy iron planet
        planet_properties = copy.deepcopy(default_planetPresets["heavy-iron-planet"])

    return planet_properties, type

def getStarTexture(temp):

    if temp > 6500: return {"namespace": "adv_rocketry","path": "textures/planet/baked_8k_sun_original.png"}

    elif temp < 4000: return {"namespace": "adv_rocketry","path": "textures/planet/baked_8k_sun_grayscale.png"}

    else: return {"namespace": "adv_rocketry","path": "textures/planet/baked_8k_sun_adjusted.png"}

def generatePlanetProperties(planetId,systemData,star_nameSpace):
    planet_data = systemData["planets"][planetId]
    star_data = systemData["star_properties"]
    temp = planet_data["temperature"]

    #planet_type = getPlanetType(planet_data["density_gcm3"])

    #print(planet_data["name"],planet_type,planet_data["density_gcm3"])

    planet_properties, planet_type = getPlanetProperties(planet_data,star_data)
    print(planet_type)
    planet_properties["description"] = f"""
        A {planet_type} in the star system {systemData["star_system"]}, {star_data["dist_LY"]} light years away from earth and {planet_data["orbital_distance"]} AU away from its Hoststar.
        Discovered in {planet_data["discovered_year"]} AD. {planet_data["link_website"]}"""

    planet_properties["name"] = planet_data["name"]
    planet_properties["generateStructures"] = False
    planet_properties["gravitationalMultiplier"] = planet_data["gravity"]
    planet_properties["orbitalDistanceToParent"] = planet_data["orbital_distance"]
    planet_properties["earthRadiusMultiplier"] = planet_data["radius"]
    planet_properties["isKnown"] = True
    planet_properties["currentTemp"] = planet_data["temperature"]

    planet_properties["parentDimensionId"] = star_nameSpace
    planet_properties["dayTimeReference"] = star_nameSpace


    planet_properties["dimensionId"] = {
        "namespace": "adv_rocketry",
        "path": to_valid_resource_location(planet_data["name"])

    }

    return planet_properties

def generateStarSystem(systemData):
    starProp = generateStarProperties(systemData)
    star_nameSpace = starProp["dimensionId"]

    objects = []
    for planetId, _ in enumerate(systemData["planets"]):
        planet_properties = generatePlanetProperties(planetId,systemData,star_nameSpace)
        objects.append(planet_properties)

    return [starProp] + objects

def convertToPlanetProp(systemsData):
    properties_arr = []
    for systemData in systemsData:
        properties_arr += generateStarSystem(systemData)
    return properties_arr

def saveToFiles(dimensionProperties):


    dimensionPropDir = Path(__file__).parent / "dimensionProperties"
    dimensionPropDir.mkdir(parents=True, exist_ok=True)

    for dimensionProperty in dimensionProperties:
        file_name = "_".join(dimensionProperty["dimensionId"].values())
        #print(file_name)
        file_path = dimensionPropDir / f"{file_name}.json"
        with open(file_path, "w", encoding="utf-8") as file:

            json.dump(dimensionProperty, file, indent=2)


starSystemsData = get_StarSystems(False,10)
dimensionProperties = convertToPlanetProp(starSystemsData)
saveToFiles(dimensionProperties)