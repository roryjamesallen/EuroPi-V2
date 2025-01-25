FROM ubuntu:22.04

ENV TERM=xterm DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    cmake git-core gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential wget python3

RUN git clone -b v1.24.1 --depth=1 --recursive https://github.com/micropython/micropython.git

WORKDIR micropython

RUN make -C ports/rp2 submodules && make -C mpy-cross clean

RUN wget https://raw.githubusercontent.com/stlehmann/micropython-ssd1306/master/ssd1306.py -O ports/rp2/modules/ssd1306.py

RUN sed -i 's/progsize=256)/progsize=1024)/g' ports/rp2/modules/_boot.py

RUN echo '\
import gc\n\
gc.collect()\n\
from contrib.menu import *\n\
BootloaderMenu(EUROPI_SCRIPTS).main()\n\
' > ports/rp2/modules/main.py

COPY software/uf2_build/copy_and_compile.sh /

WORKDIR /

ENTRYPOINT [ "sh", "copy_and_compile.sh" ]
