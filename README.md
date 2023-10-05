# Overview

Welcome to our latest project, a Python-based utility for managing save files for the game Starfield. This utility allows users to import a save file, check for its existence in the game's container path, read the container index file, and if necessary, create a new container and add the save file to it. It also provides functionalities for creating a backup of the container, writing the new container file list and index, and printing a completion message. 

# Installation

Follow these steps to install and start working with the project:

## Step 1: Prerequisites

Ensure you have the following prerequisites installed on your machine:

- Python 3.8 or later. You can download it from [here](https://www.python.org/downloads/).
- Xbox Starfield game installed on your local machine.

## Step 2: Clone the Repository

Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/HarukaMa/starfield-xgp-import.git
```

## Step 3: Navigate to the Project Directory

Navigate to the project directory using the following command:

```bash
cd starfield-xgp-import
```

## Step 4: Set the Game Path

Set the package path for the Xbox Starfield game. The path should be:

```bash
%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectGold_3275kfvn8vcwc
```

## Step 5: Run the Main Script

Finally, run the `main.py` script. You need to specify a source save file as a command line argument. Use the following command:

```bash
python main.py source_save_file
```

Replace `source_save_file` with the actual source save file.

That's it! You should now be able to use the project.
