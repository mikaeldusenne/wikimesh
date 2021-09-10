import os
from backend.src import helpers as h
from functools import cache

filepath = "backend/d2021.bin"
picklepath = "backend/mesh.pkl"

f = open(filepath, encoding="utf-8")

next(f)

line = next(f).strip()


def search(it, f, extract=lambda e: e.split('=')[-1].strip()):
    try:
        while not f((line:=next(it))):
            pass
        return extract(line)
    except StopIteration:
        return None


def parse_mesh():
    with open(filepath, encoding="utf-8") as f:
        while search(f, lambda e: e == "*NEWRECORD\n", extract=lambda e: e) is not None:
            heading = search(f, lambda e: e.startswith('MH ='))
            id = search(f, lambda e: e.startswith('UI ='))
            yield heading, id


def generate_mesh():
    mesh_data = [
        {"id": id, "title": title}
        for title, id in
        sorted(
            parse_mesh(),
            key=lambda e: ((0 if e[0][0].lower() in "azertyuiopsqdfghjklmwxcvbn" else 1), e[0])
        )
    ]
    h.save_pickle(picklepath, mesh_data)
    return mesh_data
    

@cache
def get_mesh():
    try:
        mesh_data = h.load_pickle(picklepath)
    except:
        mesh_data = generate_mesh()
    return mesh_data


if __name__ == "__main__":
    generate_mesh()
