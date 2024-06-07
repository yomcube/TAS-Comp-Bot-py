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

    return rkg[0x0D]


def get_vehicle(rkg):
    """Retrieves the vehicle ID from a given RKG file"""
    # Check if compressed and remove potential CTGP data
    if (rkg[12] & 0x08) == 0x08:
        rkg_length = struct.unpack('>I', rkg[0x88:0x8C])[0] + 0x90
        rkg = rkg[:rkg_length]

    return rkg[0x0E]


def get_track(rkg):
    """Retrieves the track ID from a given RKG file"""
    # Check if compressed and remove potential CTGP data
    if (rkg[12] & 0x08) == 0x08:
        rkg_length = struct.unpack('>I', rkg[0x88:0x8C])[0] + 0x90
        rkg = rkg[:rkg_length]

    return rkg[0x1A]


def get_controller_type(rkg):
    """Retrieves the controller type ID from a given RKG file"""
    # Check if compressed and remove potential CTGP data
    if (rkg[12] & 0x08) == 0x08:
        rkg_length = struct.unpack('>I', rkg[0x88:0x8C])[0] + 0x90
        rkg = rkg[:rkg_length]

    return rkg[0x19]


tracks = ["Luigi Circuit", "Moo Moo Meadows", "Mushroom Gorge", "Toad's Factory", "Mario Circuit", "Coconut Mall",
          "DK Summit", "Wario's Gold Mine", "Daisy Circuit", "Koopa Cape", "Maple Treeway", "Grumble Volcano",
          "Dry Dry Ruins", "Moonview Highway", "Bowser's Castle", "Rainbow Road", "GCN Peach Beach", "DS Yoshi Falls",
          "SNES Ghost Valley 2", "N64 Mario Raceway", "N64 Sherbet Land", "GBA Shy Guy Beach", "DS Delfino Square",
          "GCN Waluigi Stadium", "DS Desert Hills", "GBA Bowser Castle 3", "N64 DK's Jungle Parkway",
          "GCN Mario Circuit", "SNES Mario Circuit 3", "DS Peach Gardens", "GCN DK Mountain", "N64 Bowser's Castle"]
tracks_abbreviated = ['LC', 'MMM', 'MG', 'TF', 'MC', 'CM', 'DKSC', 'WGM', 'DC', 'KC', 'MT', 'GV', 'DDR', 'MH', 'BC',
                      'RR', 'rPB', 'rYF', 'rGV2', 'rMR', 'rSL', 'rSGB', 'rDS', 'rWS', 'rDH', 'rBC3', 'rDKJP', 'rMC',
                      'rMC3', 'rPG', 'rDKM', 'rBC']