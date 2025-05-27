# Bachelor-Thesis-Files-Skras
 Bachelor thesis simulation, renderer, progress logs and save files

## Usage instructions
Handling visualizer. render_code.java

1.In the render core set the proper directory, at which the safefile you want to preview is located. It is important for the render core to have an initialy valid save file upon starting, otherwise unexpected behavior might occur. Later on the save files can be realoaded right in the application without any problems. Note that project uses relative directores, keep that in mids.

2.To focus on a text field click on it in the app and input correct file name, without specifying the extention, simply omit it.

3.Click outside the textbox to stop focusing on it. Use arroy keys to rotate the sphere and observe the simulation in it's entirety.

4.Keep in mind that after switching the mapmode (by clicking the corresponding maptype label) you need to press any arrow key to make changes take affect (visually).

Handgling enviroment.py

1.Start simluation from there. Specigy number of turns to run the simulation in the last for loop, keep in mind that saves generate a lot of files and they have a tendency to become quite heavy so stay below a 10000 turn threthhopld unless you are prepared for it.

Handling saves
1.Use commands I gave in saves dirrectory to remerge the zipfiles provided.

2.Saves can be writen by pythonscript and their individual .json files can be additionaly studied (see report 5)

Handling screenshots
1.No special care needed. There exists few images, which were not a part of a final thesis there.

For additional questions, plese DM me.
