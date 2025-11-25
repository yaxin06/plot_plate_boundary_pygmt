#!/usr/bin/env python3
"""
Generate three PyGMT images for docs/ and write them to docs/ so they can be published.

This script is designed to run inside CI (GitHub Actions) or locally. It tries several
fallbacks if high-resolution remote data is unavailable.
"""
import os
import sys
import traceback

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "docs")
OUTDIR = os.path.abspath(OUTDIR)

os.makedirs(OUTDIR, exist_ok=True)

def save_figure(fig, name):
    path = os.path.join(OUTDIR, name)
    print(f"Saving {path}")
    fig.savefig(path)

def generate_topo():
    import pygmt
    from pygmt.datasets import load_earth_relief

    print("Generate: africa_topography.png")
    region = "-30/60/-40/40"
    # try high resolution first, then fallback
    for res in ("02m", "05m", "10m"):
        try:
            print(f"Trying resolution {res}")
            grid = load_earth_relief(resolution=res, region=region)
            fig = pygmt.Figure()
            fig.basemap(region=region, projection="M18c", frame=True)
            fig.grdimage(grid=grid, cmap="geo", shading=True)
            fig.coast(resolution="f", shorelines=True)
            fig.colorbar(frame='af+l"Elevation (m)"')
            save_figure(fig, "africa_topography.png")
            return True
        except Exception as e:
            print(f"topo res {res} failed: {e}")
            traceback.print_exc()
    return False

def generate_quakes():
    import pygmt
    from pygmt.datasets import load_earth_relief

    print("Generate: africa_quakes.png")
    region = "-30/60/-40/40"
    try:
        grid = load_earth_relief(resolution="05m", region=region)
        fig = pygmt.Figure()
        fig.grdimage(grid=grid, cmap="geo", shading=True)

        # Try to load earthquakes dataset if available, otherwise scatter synthetic points
        try:
            from pygmt.datasets import load_earthquakes
            quakes = load_earthquakes()
            print(f"Loaded {len(quakes)} earthquakes")
            fig.plot(x=quakes.longitude, y=quakes.latitude, style="cc", color="red", size="0.08c")
        except Exception:
            print("Failed to load load_earthquakes dataset; drawing example points")
            # place some example points near East Africa
            xs = [30, 36, 38, 20, 12]
            ys = [0, -3, -11, 5, 10]
            fig.plot(x=xs, y=ys, style="cc", color="red", size="0.12c")

        save_figure(fig, "africa_quakes.png")
        return True
    except Exception as e:
        print(f"generate_quakes failed: {e}")
        traceback.print_exc()
        return False

def generate_globe():
    import pygmt
    from pygmt.datasets import load_earth_relief

    print("Generate: africa_globe_hotspots.png")
    region = [-30, 60, -40, 40]
    try:
        fig = pygmt.Figure()
        fig.basemap(region=region, projection="R6c", frame=True)
        grid = load_earth_relief(resolution="05m", region=region)
        fig.grdimage(grid=grid, cmap="geo", shading=True)

        try:
            from pygmt.datasets import load_hotspots
            hotspots = load_hotspots()
            fig.plot(x=hotspots.longitude, y=hotspots.latitude, style="c0.15c", color="yellow")
        except Exception:
            print("No hotspots dataset; drawing example hotspot points")
            xs = [31, 39, 15, 50]
            ys = [-2, -10, 8, -7]
            fig.plot(x=xs, y=ys, style="c0.2c", color="yellow")

        save_figure(fig, "africa_globe_hotspots.png")
        return True
    except Exception as e:
        print(f"generate_globe failed: {e}")
        traceback.print_exc()
        return False

def main():
    ok_topo = generate_topo()
    ok_quakes = generate_quakes()
    ok_globe = generate_globe()

    total_ok = sum([ok_topo, ok_quakes, ok_globe])
    print(f"Finished: {total_ok}/3 images created in {OUTDIR}")

    # Fail the workflow if nothing was created
    if total_ok == 0:
        print("No images were produced — exiting with failure so CI can catch it.")
        sys.exit(2)

if __name__ == '__main__':
    main()
