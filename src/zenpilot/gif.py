"""recording.gif from a run's step screenshots."""

from pathlib import Path

FRAME_MS = 800


class NoPillow(Exception):
    pass


class NoSteps(Exception):
    pass


def write_gif(run_dir: Path) -> Path:
    """Write recording.gif in run_dir from its step-*.jpg, in order, sized like the first one."""
    steps = sorted(run_dir.glob("step-*.jpg"))
    if not steps:
        raise NoSteps(f"No step screenshots in {run_dir}")
    try:
        from PIL import Image
    except ImportError as e:
        raise NoPillow("Pillow isn't installed") from e
    frames = []
    for path in steps:
        try:
            with Image.open(path) as im:
                frame = im.convert("RGB")
        except OSError:  # a step file that isn't a readable image
            continue
        if frames and frame.size != frames[0].size:
            frame = frame.resize(frames[0].size)
        frames.append(frame)
    if not frames:
        raise NoSteps(f"No step screenshots in {run_dir}")
    out = run_dir / "recording.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=FRAME_MS, loop=0)
    return out
