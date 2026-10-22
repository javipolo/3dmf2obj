# 3dmf2obj

Convert QuickDraw3D text Metafiles (`.3dmf`) to [Wavefront OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file) (`.obj` + `.mtl`) so you can open them in modern 3D viewers (Blender, MeshLab, macOS Quick Look, etc.).

The old `.3dmf` format was used by Apple's QuickDraw 3D. It is awkward to open today. This script parses the **text** variant of the format and emits plain OBJ geometry plus per-mesh colors in a companion MTL file.

## Features

- Parses `TriMesh` geometry (vertices + triangle faces).
- Carries over per-mesh `DiffuseColor` into a generated `.mtl`.
- Recovers segment names from `URLElement` / `CString` records and uses them as OBJ groups.
- Handles classic Mac quirks: Mac Roman encoding and CR line endings.

> Scope: targets the LimeLight cave-survey subset of `.3dmf`. Binary `.3dmf` files are **not** supported.

## Requirements

- Python 3.6+ (standard library only, no dependencies).

## Usage

```bash
python3 3dmf2obj.py INPUT.3dmf [OUTPUT.obj]
```

If you omit the output name, it is derived from the input (`cave.3dmf` becomes `cave.obj`). The `.mtl` file is written next to the `.obj`.

```bash
# Explicit output
python3 3dmf2obj.py cave.3dmf cave.obj

# Output defaults to cave.obj + cave.mtl
python3 3dmf2obj.py cave.3dmf

# Quiet mode (no progress output)
python3 3dmf2obj.py -q cave.3dmf
```

### Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help and exit. |
| `-q`, `--quiet` | Suppress progress output. |
| `--version` | Show version and exit. |

### Make it executable (optional)

```bash
chmod +x 3dmf2obj.py
./3dmf2obj.py cave.3dmf
```

## Output

Two files are produced:

- `OUTPUT.obj` — geometry, one group (`g`) per mesh with its `usemtl`.
- `OUTPUT.mtl` — one material per mesh carrying the diffuse color.

Open the `.obj` in any modern viewer; the `.mtl` is picked up automatically as long as the two files stay in the same directory.

## License

GNU General Public License v3.0 or later. See [LICENSE](LICENSE).
