framboise
=========

Utility to download subtitles timely from opensubtitles.org

Basic Usage
------------

	framboise <videos files and/or directories> -l lang,lang,...

framboise check your videos directory recursivelly for all videos, find 
all subtitles from opensubtitles that match each video and then choses 
the best one for you.

You can add several language IDs to framboise. Example

	framboise Videos/Movies -l por,pob,esp,oci,eng

This will look for every video under `Videos/Movies` and find all 
subtitles in Portuguese, Brazilian Portuguese, Spanish, Occitan and 
English. It will choose a subtitle among the first language (in that 
order) that found matches. 

If several subtitles for a same language match, framboise will choose 
the one of which's filename is more similar to your video filename.

Help welcome!
-------------

framboise is a work in progress. If you'd like to help, feel free to 
fork and send me a push request. Just remember, if you add any feature:

- It must be simple to use 
- It must be light (should be able to run on a raspberry pi) 
- Code should be easily understandable (please do not turn python into 
  haskell)

Why the name?
-------------

I needed to have a lightweight tool to automatically download subtitles 
to movies I had set up on my raspberry pi. Framboise is raspberry in French.

Interesting ideas to implement
------------------------------

1. If a subtitle is found, check if there is a better suited subtitle (a 
   preferred language among the choices)
2. Also, if a subtitle is found, send it to opensubtitles if not there
3. A flexget plugin to download subtitles based on this

