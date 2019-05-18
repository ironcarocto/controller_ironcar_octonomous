[![Build Status](https://travis-ci.org/ironcarocto/controller_ironcar_octonomous.svg?branch=master)](https://travis-ci.org/ironcarocto/controller_ironcar_octonomous)

# Controller Ironcar Octonomous

Octonomous est une voiture maintenue par Octo Technology pour l'ironcar.
Ce programme est utilisé pour conduire la voiture en étabilissant
des inférences à partir de la caméra et d'un modèle de deeplearning.

[Ironcar](http://ironcar.org/) est un championnat de courses de voitures
autonomes en modèle réduit !

## Run it !

Run the controller
 
```console
$ controller_ironcar
``` 

```bash
controller_ironcar [-h] [--resolution RESOLUTION RESOLUTION]
                         [--model-path PATH] [--speed SPEED] [--preview]
                         [--regression] [--log-level LOGLEVEL]
```

where :
* -h: prints the help message
* --resolution / -r: the resolution (width height) of the camera. You must 
pass 2 integers after the `--resolution` option - for example, 
`--resolution 100 50`. Default = 240 176
* --model-path / -m: absolute path to the Keras model. `keras.load_model` will 
be used to load the model, which must comply with this function requirements 
(if you used keras to save your model, you should be fine). 
Default = '/home/pi/ironcar/autopilots/octo240x123_nvidia.hdf5'
* --speed / -s: the ratio (from 0 to 1) of the max speed to be used. 1 means 
that the IronCar will be allowed to use the maximum hardware speed (which is 
very fast, start with a low value such as 0.2) Default = 0.2
* --preview / -p: prints a preview of the picamera directly onto the terminal. 
Neat, but you probably don't want that in production.
* --regression / -R: assume a regression model (default is classification)
* --log-level / -l: the log level used (from CRITICAL to DEBUG). Default = INFO

## Hardware setup

You will find a tutorial on google docs [here](https://docs.google.com/document/d/1jyRhlbmthMA_DuuulYnzUT38okIF_KFZH0a4hh8NCg8/edit?usp=sharing)  .

## Raspberry-pi Setup

### Easy setup with install.sh

You can easily setup everything on the raspi using the `install.sh` bash. To do so, go on your raspi and do:
``` sh
$ ./install.sh
```

It will install *keras*, *tensorflow*, *nodejs* and some other dependencies in the requirements. This should take 2-3 hours... (*scipy* is very long to install). At the end of the install, you will need to choose if you want to enable the pi camera, i2c connections and augment the swap size (which is very small by default). 
And that's it, you should be ready to go to the launching part!!

### Manual setup

1. clone the repository

```bash
git clone https://github.com/ironcarocto/controller_ironcar_octonomous
```

2. install the package

```bash
pip3 install .[raspberry]
```