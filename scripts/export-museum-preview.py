"""Export a public, terrain-only 1.21.1 museum or Full Tour world."""

import argparse
import gzip
import hashlib
import io
import json
import struct
import zlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import nbtlib


SECTOR = 4096
DATA_VERSION = 3955
LEVEL_FIELDS = ("Version", "DataVersion", "version", "WorldGenSettings", "initialized")
CHUNK_FIELDS = (
    "DataVersion", "Status", "xPos", "yPos", "zPos", "sections", "Heightmaps", "isLightOn",
)
REPLACE_BLOCKS = {
    "mujobots:robot_pedestal": "minecraft:smooth_stone",
    "minecraft:command_block": "minecraft:air",
    "minecraft:chain_command_block": "minecraft:air",
    "minecraft:repeating_command_block": "minecraft:air",
    "minecraft:structure_block": "minecraft:air",
}
MUSEUM = {
    "name": "MujoVerse Museum - Web Preview",
    "entrance": (0.5, 65, 21.5),
    "chunks": (range(-5, 5), range(-8, 5)),
    "replace": REPLACE_BLOCKS,
    "required": {"minecraft:quartz_pillar", "minecraft:cyan_terracotta"},
}
FULL_TOUR = {
    "name": "MujoVerse Full Tour - Web Preview",
    "entrance": (0.5, -60, 20.5),
    # All 11 station floors (centers x=0..800, z=0) and the connecting paths.
    "chunks": (range(-4, 55), range(-4, 4)),
    "replace": {**REPLACE_BLOCKS, "minecraft:stone_button": "minecraft:air",
                "minecraft:oak_wall_sign": "minecraft:air"},
    "required": {"minecraft:smooth_quartz", "minecraft:green_concrete",
                 "minecraft:yellow_concrete", "minecraft:sea_lantern"},
}


def encode_nbt(root):
    out = io.BytesIO()
    root.write(out)
    return out.getvalue()


def export_level(path, world):
    original = nbtlib.load(path)["Data"]
    if original["DataVersion"] != DATA_VERSION:
        raise ValueError("Expected a Minecraft Java 1.21.1 save")
    generator = original["WorldGenSettings"]["dimensions"]["minecraft:overworld"]["generator"]
    if generator["type"] != "minecraft:flat":
        raise ValueError("Expected a built superflat demo world")
    entrance = world["entrance"]
    data = nbtlib.Compound({key: original[key] for key in LEVEL_FIELDS})
    data.update(
        LevelName=nbtlib.String(world["name"]),
        SpawnX=nbtlib.Int(entrance[0]),
        SpawnY=nbtlib.Int(entrance[1]),
        SpawnZ=nbtlib.Int(entrance[2]),
        SpawnAngle=nbtlib.Float(180),
        generatorName=nbtlib.String("flat"),
        GameType=nbtlib.Int(2),
        Difficulty=nbtlib.Byte(0),
        Time=nbtlib.Long(6000),
        DayTime=nbtlib.Long(6000),
        allowCommands=nbtlib.Byte(0),
        hardcore=nbtlib.Byte(0),
        DataPacks=nbtlib.Compound({
            "Enabled": nbtlib.List[nbtlib.String](["vanilla"]),
            "Disabled": nbtlib.List[nbtlib.String]([]),
        }),
        GameRules=nbtlib.Compound({
            "doDaylightCycle": nbtlib.String("false"),
            "doMobSpawning": nbtlib.String("false"),
            "spawnRadius": nbtlib.String("0"),
        }),
        # Flying Squid v0.0.122 converts the saved yaw from 256 units per turn.
        Player=nbtlib.Compound({
            "Health": nbtlib.Float(20),
            "foodLevel": nbtlib.Int(20),
            "playerGameType": nbtlib.Int(2),
            "XpTotal": nbtlib.Int(0),
            "SelectedItemSlot": nbtlib.Int(0),
            "Dimension": nbtlib.String("minecraft:overworld"),
            "Pos": nbtlib.List[nbtlib.Double](entrance),
            "Rotation": nbtlib.List[nbtlib.Float]([128, 0]),
            "OnGround": nbtlib.Byte(1),
            "abilities": nbtlib.Compound({"flying": nbtlib.Byte(0)}),
            "Inventory": nbtlib.List[nbtlib.Compound]([]),
        }),
    )
    return gzip.compress(encode_nbt(nbtlib.File({"Data": data})), mtime=0)


def export_region(source, x_region, z_region, world):
    header = bytearray(2 * SECTOR)
    body = bytearray()
    blocks = set()
    chunk_x, chunk_z = world["chunks"]
    for z in chunk_z:
        for x in chunk_x:
            if (x // 32, z // 32) != (x_region, z_region):
                continue
            slot = ((z % 32) * 32 + x % 32) * 4
            sector = int.from_bytes(source[slot:slot + 3], "big")
            if sector < 2:
                raise ValueError(f"Missing demo chunk at {x},{z}")
            start = sector * SECTOR
            length, codec = struct.unpack_from(">IB", source, start)
            if codec != 2:
                raise ValueError(f"Unsupported compression {codec} in chunk {x},{z}")
            chunk = nbtlib.File.parse(io.BytesIO(zlib.decompress(source[start + 5:start + 4 + length])))
            if (chunk["DataVersion"], chunk["xPos"], chunk["zPos"], chunk["Status"]) != (
                DATA_VERSION, x, z, "minecraft:full",
            ):
                raise ValueError(f"Unexpected chunk metadata at {x},{z}")
            for section in chunk["sections"]:
                for state in section.get("block_states", {}).get("palette", []):
                    name = str(state["Name"])
                    if name in world["replace"]:
                        state.clear()
                        state["Name"] = nbtlib.String(world["replace"][name])
                    elif not name.startswith("minecraft:"):
                        raise ValueError(f"Non-vanilla block {name} in chunk {x},{z}")
                    blocks.add(str(state["Name"]))
            clean = nbtlib.File({key: chunk[key] for key in CHUNK_FIELDS if key in chunk})
            # Keep terrain and light, never block-entity payloads, ticks, or scripts.
            clean["block_entities"] = nbtlib.List[nbtlib.Compound]([])
            clean["structures"] = nbtlib.Compound()
            clean["LastUpdate"] = nbtlib.Long(0)
            clean["InhabitedTime"] = nbtlib.Long(0)
            compressed = zlib.compress(encode_nbt(clean), 9)
            record = struct.pack(">IB", len(compressed) + 1, 2) + compressed
            count = (len(record) + SECTOR - 1) // SECTOR
            header[slot:slot + 4] = (2 + len(body) // SECTOR).to_bytes(3, "big") + bytes([count])
            body.extend(record.ljust(count * SECTOR, b"\0"))
    return header + body, blocks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("save", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--full-tour", action="store_true", help="export the standalone 11-station playtest save")
    args = parser.parse_args()
    world = FULL_TOUR if args.full_tour else MUSEUM
    if args.full_tour:
        marker = args.save / "mujotour-built.json"
        if not marker.is_file() or json.loads(marker.read_text(encoding="utf-8")).get("zones") != 11:
            raise ValueError("Expected the built MujoVerse Full Tour save with 11 stations")
    if any(path.resolve().is_relative_to(args.save.resolve())
           for path in (args.output, args.output.with_suffix(""))):
        raise ValueError("Write the preview outside the source save")
    files = {"level.dat": export_level(args.save / "level.dat", world)}
    blocks = set()
    chunk_x, chunk_z = world["chunks"]
    for x, z in sorted({(x // 32, z // 32) for x in chunk_x for z in chunk_z}):
        name = f"region/r.{x}.{z}.mca"
        files[name], region_blocks = export_region((args.save / name).read_bytes(), x, z, world)
        blocks.update(region_blocks)
    if not world["required"] <= blocks:
        raise ValueError(f"The cropped area does not contain {world['name']}")
    # The client can fetch this read-only index regardless of the host's ZIP MIME type.
    directory = args.output.with_suffix("")
    index = {"level.dat": None, "region": {}}
    for name, contents in files.items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents)
        if name.startswith("region/"):
            index["region"][target.name] = None
    (directory / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="ascii")
    archive = io.BytesIO()
    with ZipFile(archive, "w") as zipped:
        for name, contents in files.items():
            zipped.writestr(ZipInfo(name), contents, compress_type=ZIP_DEFLATED, compresslevel=9)
    payload = archive.getvalue()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"{len(chunk_x) * len(chunk_z)} chunks, {len(files)} files, {len(payload)} bytes")
    print(f"SHA-256 {hashlib.sha256(payload).hexdigest()}")


if __name__ == "__main__":
    main()
