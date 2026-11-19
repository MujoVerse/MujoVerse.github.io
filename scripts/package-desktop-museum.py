"""Build the desktop museum save and Modrinth pack from pinned release inputs."""

import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile
import zlib

import nbtlib


WORLD = "MujoVerse Museum"
PACK = "MujoVerse-Museum-1.21.1-preview.1"
DATAPACK = "mujobots_museum"
API = "fabric-api-0.116.17+1.21.1.jar"
API_SHA1 = "810b2b0195371a012906241d8b85a32a1d6de53c"
API_SHA512 = ("98c478217da19181f0e4df3ea6c2da6bdbda271c7544a4aea048513a49b444f1ff5b"
              "71dc0df6303017c48e8ff69b7bb6af6179bdf0d0e09ab3c1ee08411857a8")
API_URL = "https://cdn.modrinth.com/data/P7dR8mSH/versions/Mys3P7lK/fabric-api-0.116.17%2B1.21.1.jar"
JARS = (
    "mujocraft-0.3.1.jar", "mujobots-0.5.0.jar", "minepilot-0.1.0.jar", "minearena-0.1.0.jar",
    "mujobots-exhibits-0.5.0.jar", "mujobots-g1-0.5.0.jar", "mujobots-go1-0.5.0.jar",
    "mujobots-onnxruntime-1.31.1.jar",
)
REGIONS = ("r.-1.-1.mca", "r.-1.0.mca", "r.0.-1.mca", "r.0.0.mca")
SECTOR = 4096


def read_region(data):
    for slot in range(0, SECTOR, 4):
        start = int.from_bytes(data[slot:slot + 3], "big") * SECTOR
        if not start:
            continue
        length, method = struct.unpack_from(">IB", data, start)
        if method != 2:
            raise ValueError(f"Unexpected region compression {method}")
        raw = zlib.decompress(data[start + 5:start + 4 + length])
        yield slot, nbtlib.File.parse(io.BytesIO(raw))


def encode_region(chunks):
    header = bytearray(2 * SECTOR)
    body = bytearray()
    for slot, chunk in chunks:
        output = io.BytesIO()
        chunk.write(output)
        payload = zlib.compress(output.getvalue(), 9)
        record = struct.pack(">IB", len(payload) + 1, 2) + payload
        count = (len(record) + SECTOR - 1) // SECTOR
        header[slot:slot + 4] = (2 + len(body) // SECTOR).to_bytes(3, "big") + bytes([count])
        body.extend(record.ljust(count * SECTOR, b"\0"))
    return header + body


def clean_entities(data, counts, exhibit_ids):
    for slot, chunk in read_region(data):
        keep = []
        for entity in chunk["Entities"]:
            kind = str(entity["id"])
            if kind == "mujobots:exhibit":
                robot = str(entity["robot"])
                if robot in {"booster_k1", "booster_t1"}:
                    robot += "_exhibit"
                    entity["robot"] = nbtlib.String(robot)
                if robot not in exhibit_ids:
                    raise ValueError(f"Exhibit is not in the bundled pack: {robot}")
            if kind == "minecraft:item_frame":
                item = entity.get("Item", {})
                if item.get("id") == "mujobots:exhibit_capsule":
                    item["id"] = nbtlib.String("mujobots:robot_capsule")
                if item.get("id") == "mujobots:t2_remote":
                    item["id"] = nbtlib.String("mujobots:robot_remote")
            if kind == "minecraft:text_display":
                x, y, z = map(float, entity["Pos"])
                label = None
                if abs(x - 37.5) < .01 and abs(z + 63.4) < .01:
                    label = {"text": "召唤 Go1 / Spawn Go1", "color": "#F2D7A0"}
                elif abs(x - 39.5) < .01 and abs(y - 68.4) < .01 and abs(z + 63.4) < .01:
                    label = {"text": "实时物理 / Live physics\nUnitree G1 + Go1", "color": "#3FD8C8"}
                elif abs(x - 27) < .01 and abs(z + 7.97) < .01:
                    label = {"text": "MujoBots\nG1 / Go1 Physics\n33 Robot Exhibits", "color": "#3FD8C8"}
                if label:
                    entity["text"] = nbtlib.String(json.dumps(label, ensure_ascii=False))
            if kind not in {"minecraft:text_display", "minecraft:block_display",
                            "minecraft:item_frame", "mujobots:exhibit"}:
                continue
            counts[kind] += 1
            keep.append(entity)
        if not keep:
            continue
        chunk["Entities"] = nbtlib.List[nbtlib.Compound](keep)
        yield slot, chunk


def select(robot):
    return f'@e[type=mujobots:robot,x=34,y=63,z=-82,dx=10,dy=12,dz=16,nbt={{robot:"{robot}"}}]'


def clean_terrain(data, commands):
    for slot, chunk in read_region(data):
        for entity in chunk.get("block_entities", []):
            if "Command" not in entity:
                continue
            command = str(entity["Command"])
            commands.append(command)
            for function, robot, x in (("live_g1", "g1", 37.5), ("live_t2", "unitree_go1", 41.5)):
                if command == f"execute positioned 37.5 65 -74.5 run function museum:{function}":
                    entity["Command"] = nbtlib.String(
                        f"execute unless entity {select(robot)} run mujobots spawn {robot} {x} 65 -74.5 0"
                    )
            for key in ("LastOutput", "LastExecution"):
                entity.pop(key, None)
        yield slot, chunk


def museum_files(save, exhibit_ids):
    level = nbtlib.load(save / "level.dat")
    data = level["Data"]
    if data["DataVersion"] != 3955:
        raise ValueError("Expected a Minecraft Java 1.21.1 save")
    # Keep world generation and rules; do not ship the author's player or server state.
    fields = ("DataVersion", "version", "Version", "WorldGenSettings", "initialized",
              "GameRules", "DataPacks", "DragonFight")
    world = nbtlib.Compound({key: data[key] for key in fields})
    world.update(LevelName=nbtlib.String(WORLD), SpawnX=nbtlib.Int(0), SpawnY=nbtlib.Int(65),
                 SpawnZ=nbtlib.Int(22), SpawnAngle=nbtlib.Float(180), GameType=nbtlib.Int(2),
                 allowCommands=nbtlib.Byte(1), Difficulty=nbtlib.Byte(0),
                 Time=nbtlib.Long(6000), DayTime=nbtlib.Long(6000))
    world["GameRules"].update(spawnRadius=nbtlib.String("0"), sendCommandFeedback=nbtlib.String("true"))
    world["DataPacks"]["Enabled"] = nbtlib.List[nbtlib.String](["vanilla", f"file/{DATAPACK}"])
    output = io.BytesIO()
    nbtlib.File({"Data": world}).write(output)
    yield "level.dat", gzip.compress(output.getvalue(), mtime=0)

    counts = Counter()
    commands = []
    for name in REGIONS:
        terrain = (save / "region" / name).read_bytes()
        yield f"region/{name}", encode_region(clean_terrain(terrain, commands))
        entities = (save / "entities" / name).read_bytes()
        yield f"entities/{name}", encode_region(clean_entities(entities, counts, exhibit_ids))
    expected = {
        "function museum:reset_towers",
        "give @p[distance=..6] mujocraft:assembly_wand",
        "give @p[distance=..6] mujocraft:physics_hammer",
        *(f"execute positioned 37.5 65 -74.5 run function museum:{fn}"
          for fn in ("live_g1", "live_t2", "live_stop", "live_walk", "live_clear")),
    }
    if sorted(commands) != sorted(expected) or counts["mujobots:exhibit"] != 41:
        raise ValueError(f"Unexpected museum contents: exhibits={counts}, commands={commands}")

    root = f"datapacks/{DATAPACK}"
    yield f"{root}/pack.mcmeta", b'{"pack":{"pack_format":48,"description":"MujoVerse desktop museum"}}\n'
    original_reset = save / root / "data/museum/function/reset_towers.mcfunction"
    reset = """kill @e[type=mujocraft:structure,x=20,y=65,z=-62,dx=12,dy=20,dz=10]
fill 21 65 -61 31 75 -53 air
clone 20 35 -62 32 43 -52 20 65 -62
mujocraft assemble 22 65 -60 23 70 -59
mujocraft assemble 26 65 -60 27 69 -59
mujocraft assemble 30 65 -60 31 68 -59
mujocraft assemble 22 65 -55 23 67 -54
mujocraft assemble 26 65 -55 27 68 -54
mujocraft assemble 30 65 -55 31 69 -54
"""
    if original_reset.read_text(encoding="utf-8").splitlines() != reset.splitlines():
        raise ValueError("Source tower layout does not match")
    functions = {
        "reset_towers": reset.rstrip(),
        "live_walk": f"mujobots walk {select('g1')} 0.3 0 0\nmujobots walk {select('unitree_go1')} 0.35 0 0",
        "live_stop": f"mujobots stop {select('g1')}\nmujobots stop {select('unitree_go1')}",
        "live_clear": f"kill {select('g1')}\nkill {select('unitree_go1')}",
    }
    # Recreate the six initial towers once, then leave reset available on its button.
    functions["init"] = ("forceload add 20 -62 32 -52\n"
                         "schedule function museum:first_towers 2s")
    functions["first_towers"] = ("function museum:reset_towers\n"
                                 "forceload remove 20 -62 32 -52\n"
                                 "scoreboard players set #built museum_init 1")
    functions["load"] = ("scoreboard objectives add museum_init dummy\n"
                         "execute unless score #built museum_init matches 1 run function museum:init")
    yield f"{root}/data/minecraft/tags/function/load.json", b'{"values":["museum:load"]}\n'
    for name, text in functions.items():
        yield f"{root}/data/museum/function/{name}.mcfunction", (text + "\n").encode()
    print(f"Preserved museum entities: {dict(counts)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("save", type=Path)
    parser.add_argument("mod_directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    receipt = json.loads((args.mod_directory.parent / "build-receipt.json").read_text(encoding="utf-8-sig"))
    digests = {item["file"]: item["sha256"].lower() for item in receipt["runtimeArtifacts"]}
    for name in JARS:
        jar = args.mod_directory / name
        with jar.open("rb") as source:
            if hashlib.file_digest(source, "sha256").hexdigest() != digests[name]:
                raise ValueError(f"Unverified release jar: {name}")
    with ZipFile(args.mod_directory / "mujobots-exhibits-0.5.0.jar") as exhibits:
        exhibit_ids = {json.loads(exhibits.read(name))["id"] for name in exhibits.namelist()
                       if name.startswith("assets/mujobots/exhibits/") and name.endswith("/robot.json")}
    files = dict(museum_files(args.save, exhibit_ids))
    index = {
        "formatVersion": 1, "game": "minecraft", "versionId": "1.21.1-preview.1",
        "name": WORLD, "summary": "Museum, robot exhibits and live MuJoCo physics.",
        "dependencies": {"minecraft": "1.21.1", "fabric-loader": "0.16.10"},
        "files": [{"path": f"mods/{API}", "hashes": {"sha1": API_SHA1, "sha512": API_SHA512},
                   "downloads": [API_URL], "fileSize": 2452735, "env": {"client": "required", "server": "required"}}],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output / f"{PACK}-world.zip", "w", ZIP_DEFLATED) as zipped:
        for name, contents in files.items():
            zipped.writestr(f"{WORLD}/{name}", contents)
    with ZipFile(args.output / f"{PACK}.mrpack", "w", ZIP_DEFLATED) as zipped:
        zipped.writestr("modrinth.index.json", json.dumps(index, indent=2))
        for name, contents in files.items():
            zipped.writestr(f"overrides/saves/{WORLD}/{name}", contents)
        for name in JARS:
            zipped.write(args.mod_directory / name, f"overrides/mods/{name}", ZIP_STORED)
    for result in sorted(args.output.glob(f"{PACK}*")):
        with result.open("rb") as source:
            print(f"{hashlib.file_digest(source, 'sha256').hexdigest()}  {result.name}")


if __name__ == "__main__":
    main()
