# Hammerbeam Slideshow

This is a zmk module to implement a slideshow of images on the peripheral (right) nice!view display.

Hammerbeam, _the original artist of the iconic balloon and mountain art found in the default zmk firmware for the nice!view screen_, has more fantastic 1 bit art that you may not have seen.

With Hammerbeam's consent, he allowed me use what I wanted of his public posts of his 1-bit art and format them as necessary to bring more of his work to the nice!view display. I made sure to keep his signature in each picture for attribution so others can find more of his work.

## NEW: Automated Art Generation

This project now includes an automated art generation system! You can easily create your own custom slideshows:

```bash
# Quick start - handles everything automatically!
make setup              # Install dependencies
cp your_images/* art/   # Add your images (any names)
make generate           # Auto-rename + generate slideshow
```

**[Complete Art Generation Guide →](ART_GENERATION.md)**

## Features

- **Custom Art Support**: Generate slideshows from your own images
- **Automated Processing**: Resize and convert images to 1-bit format
- **Easy Workflow**: Simple Makefile commands for everything
- **Safety Features**: Automatic backups and validation
- **Perfect Fit**: Optimized for 68×140 nice!view display (vertical)

The picture displayed on the peripheral screen changes every 10 seconds by default.

## Current Slideshow Preview

![Slideshow Preview](./assets/slideshow_preview.png)

*The above shows all images in your current slideshow (auto-generated after running `make generate`)*

## Original Hammerbeam Art

![art](./assets/hammerbeam.png)

![art](./assets/20240913_193934.png)

## Usage

To use this module, first add it to your config/west.yml by adding a new entry to remotes and projects:

```yml
manifest:
  remotes:
      # zmk official
    - name: zmkfirmware
      url-base: https://github.com/zmkfirmware
    - name: gpeye                         #new entry
      url-base: https://github.com/GPeye  #new entry
  projects:
    - name: zmk
      remote: zmkfirmware
      revision: main
      import: app/west.yml
    - name: hammerbeam-slideshow          #new entry
      remote: gpeye                       #new entry
      revision: main                      #new entry
  self:
    path: config
```

Now simply swap out the default nice_view shield on the board for the custom one in your build.yaml file.

```yml
---
include:
  - board: nice_nano_v2
    shield: urchin_left nice_view_adapter  nice_view
  - board: nice_nano_v2
    shield: urchin_right nice_view_adapter nice_view_custom #custom shield
```

By default this animation will run for a duration of 300 seconds (10 seconds per picture) to save battery.

If you want to change the speed of the animation, you can edit the speed by changing the CONFIG_CUSTOM_ANIMATION_SPEED in your .conf file

For example:

```conf
# config.conf
CONFIG_CUSTOM_ANIMATION_SPEED=300000 # 300 second total duration
# With 30 pictures, that's 10 seconds per picture
```

## Art Generation Commands

| Command | What it does |
|---------|-------------|
| `make help` | Show all available commands |
| `make setup` | Install dependencies and create folders |
| `make generate` | Create slideshow from your images |
| `make info` | Show project status |
| `make backup` | Backup current files |
| `make restore` | Restore from backup |

## Requirements

- Python 3.7+
- Pillow (PIL) for image processing
- Make (for convenient commands)

## Contributing

Found a bug or want to add features? Contributions welcome! The art generation system is designed to be easily extensible.