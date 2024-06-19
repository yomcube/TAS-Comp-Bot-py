import struct


def get_lap_time(rkg):
    """Retrieves the lap times of all laps of a given RKG file"""
    # Check if compressed and remove potential CTGP data
    if (rkg[12] & 0x08) == 0x08:
        rkg_length = struct.unpack('>I', rkg[0x88:0x8C])[0] + 0x90
        rkg = rkg[:rkg_length]

    # Extract the number of laps
    nr_laps = rkg[0x10]
    lap_times = []
    for i in range(nr_laps):
        min = rkg[0x11 + i * 3] >> 1
        sec = ((rkg[0x11 + i * 3] & 0x1) << 6) | (rkg[0x12 + i * 3] >> 2)
        mil = ((rkg[0x12 + i * 3] & 0x3) << 8) | rkg[0x13 + i * 3]
        lap_times.append(f"{min}:{sec:02}.{mil:03}")
    return lap_times


def get_character(rkg):
    """Retrieves the character ID from a given RKG file"""
    # Check if compressed and remove potential CTGP data
    if (rkg[12] & 0x08) == 0x08:
        rkg_length = struct.unpack('>I', rkg[0x88:0x8C])[0] + 0x90
        rkg = rkg[:rkg_length]

    return (rkg[0x8] & 0x3) << 0x4 | (rkg[0x9]) >> 0x4


def get_vehicle(rkg):
    """Retrieves the vehicle ID from a given RKG file"""
    # Check if compressed and remove potential CTGP data
    if (rkg[12] & 0x08) == 0x08:
        rkg_length = struct.unpack('>I', rkg[0x88:0x8C])[0] + 0x90
        rkg = rkg[:rkg_length]

    return rkg[0x8] >> 0x2





tracks = ["Luigi Circuit", "Moo Moo Meadows", "Mushroom Gorge", "Toad's Factory", "Mario Circuit", "Coconut Mall",
          "DK Summit", "Wario's Gold Mine", "Daisy Circuit", "Koopa Cape", "Maple Treeway", "Grumble Volcano",
          "Dry Dry Ruins", "Moonview Highway", "Bowser's Castle", "Rainbow Road", "GCN Peach Beach", "DS Yoshi Falls",
          "SNES Ghost Valley 2", "N64 Mario Raceway", "N64 Sherbet Land", "GBA Shy Guy Beach", "DS Delfino Square",
          "GCN Waluigi Stadium", "DS Desert Hills", "GBA Bowser Castle 3", "N64 DK's Jungle Parkway",
          "GCN Mario Circuit", "SNES Mario Circuit 3", "DS Peach Gardens", "GCN DK Mountain", "N64 Bowser's Castle"]
tracks_abbreviated = ['LC', 'MMM', 'MG', 'TF', 'MC', 'CM', 'DKSC', 'WGM', 'DC', 'KC', 'MT', 'GV', 'DDR', 'MH', 'BC',
                      'RR', 'rPB', 'rYF', 'rGV2', 'rMR', 'rSL', 'rSGB', 'rDS', 'rWS', 'rDH', 'rBC3', 'rDKJP', 'rMC',
                      'rMC3', 'rPG', 'rDKM', 'rBC']



characters = {
    0: "Mario",
    1: "Baby Peach",
    2: "Waluigi",
    3: "Bowser",
    4: "Baby Daisy",
    5: "Dry Bones",
    6: "Baby Mario",
    7: "Luigi",
    8:"Toad",
    9: "Donkey Kong",
    10: "Yoshi",
    11: "Wario",
    12: "Baby Luigi",
    13: "Toadette",
    14: "Koopa Troopa",
    15: "Daisy",
    16: "Peach",
    17: "Birdo",
    18: "Diddy Kong",
    19: "King Boo",
    20: "Bowser Jr.",
    21: "Dry Bowser",
    22: "Funky Kong",
    23: "Rosalina",
    24: "Small Mii Outfit A (Male)",
    25: "Small Mii Outfit A (Female)",
    26: "Small Mii Outfit B (Male)",
    27: "Small Mii Outfit B (Female)",
    28: "Small Mii Outfit C (Male)",
    29: "Small Mii Outfit C (Female)",
    30: "Medium Mii Outfit A (Male)",
    31: "Medium Mii Outfit A (Female)",
    32: "Medium Mii Outfit B (Male)",
    33: "Medium Mii Outfit B (Female)",
    34: "Medium Mii Outfit C (Male)",
    35: "Medium Mii Outfit C (Female)",
    36: "Large Mii Outfit A (Male)",
    37: "Large Mii Outfit A (Female)",
    38: "Large Mii Outfit B (Male)",
    39: "Large Mii Outfit B (Female)",
    40: "Large Mii Outfit C (Male)",
    41: "Large Mii Outfit C (Female)",
    42: "Medium Mii",
    43: "Small Mii",
    44: "Large Mii",
    45: "Peach Biker Outfit",
    46: "Daisy Biker Outfit",
    47: "Rosalina Biker Outfit"
}

vehicles = {
    0: "Standard Kart S",
    1: "Standard Kart M",
    2: "Standard Kart L",
    3: "Baby Booster",
    4: "Classic Dragster",
    5: "Offroader",
    6: "Mini Beast",
    7: "Wild Wing",
    8: "Flame Flyer",
    9: "Cheep Charger",
    10: "Super Blooper",
    11: "Piranha Prowler",
    12: "Rally Romper",
    13: "Daytripper",
    14: "Jetsetter",
    15: "Blue Falcon",
    16: "Sprinter",
    17: "Honeycoupe",
    18: "Standard Bike S",
    19: "Standard Bike M",
    20: "Standard Bike L",
    21: "Bullet Bike",
    22: "Mach Bike",
    23: "Flame runner",
    24: "Bit Bike",
    25: "Sugarscoot",
    26: "Wario Bike",
    27: "Quacker",
    28: "Zip Zip",
    29: "Shooting Star",
    30: "Magikruiser",
    31: "Sneakster",
    32: "Spear",
    33: "Jet Bubble",
    34: "Dolphin Dasher",
    35: "Phantom"
}
