# Pulicam
This is a quick 'n dirty script for setting up a Raspberry Pi camera web server.

I did most of the work programming in my phone on a sleepless night so it's a
very basic code, but it works.

This script is designed to run under Python 3, there are some things (like the
crypt module) that changed between Python 2 and 3 so if you want to use Python 2
some changes are needed.

## Requirements
- python3-pigpio

Optional:
- raspistill (well, this is really a requirement since is the way you will
  gather an image from the camera but is not a 'code' requirement)
- supervisord
- gunicorn

## TODO
- [ ] Add some style sheets (maybe just use a minimal bootstrap style)
- [ ] Make movement and memory calls asynchronous

## LICENSE
Copyright (C) 2017  Sergio Conde Gómez <skgsergio[at]gmail[dot]com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
