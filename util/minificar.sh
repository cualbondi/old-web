#!/bin/sh

#cd cualbondi's git root
java -jar util/closure-compiler.jar --js media/js/functions-2.0.js --js_output_file media/js/functions-2.0.js
java -jar util/closure-compiler.jar --js media/js/vr-1.0.js --js_output_file media/js/vr-1.0.js
