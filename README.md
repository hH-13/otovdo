# Trendy Short Video Generator

A Python project to automatically create engaging short videos in the style of TikTok, YouTube Shorts, and Instagram Reels.

## Features

- Generate short videos from scratch using images, video clips, and audio
- Add trendy effects, transitions, and text overlays
- Supports vertical (9:16) video format
- Customizable templates for different social platforms
## Installation

```bash
uv pip install .
```

Or, if you want to install dependencies for development:

```bash
uv pip install -e .[dev]
```

## Usage

```bash
python -m otovdo --input assets/ --output output/video.mp4
```

## Requirements

All dependencies are specified in `pyproject.toml`. Key requirements include:

- Python 3.8+
- moviepy
- opencv-python
- numpy

Install them automatically with the installation commands above.

## Example

![Demo Screenshot](docs/demo.gif)

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.