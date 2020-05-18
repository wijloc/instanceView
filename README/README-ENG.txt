/*** evaluate_fastest_path ***/

1)	PRELIMINARY INSTALLATIONS

	a.	install homebrew directly from terminal using the following command:

		|------------|
		|   MAC OS   |
		|------------|

		/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

		--------------------------------------------------------------------------------------------------------------------------------------------------

		Reference: https://brew.sh/

		--------------------------------------------------------------------------------------------------------------------------------------------------

2)	INSTALL AND CONFIGURE OPEN SOURCE ROUTING MACHINE (OSRM)

	a.	you need to have enough RAM memory to install OSRM, it is not recommended to install it on a virtual machine

		Reference issue in case of compiling error: https://github.com/Project-OSRM/osrm-backend/issues/1151

	b.	run the following commands from terminal:

		|------------|
		|   MAC OS   |
		|------------|

		brew update

		brew install cmake

		brew install boost git libzip libstxxl libxm12 (IT GIVES ERRORS) lua tbb ccache
		
		brew install GDAL

	c.	download osrm-backend project from Git Hub using the following command:

		brew install osrm-backend

		|--------------|
        |    UBUNTU    |
        |--------------|

		git clone https://github.com/Project-OSRM/osrm-backend.git

		--------------------------------------------------------------------------------------------------------------------------------------------------

	c.	access the osrm-backend folder you have just downloaded using the following commands:

		|-----------------------|
		|    UBUNTU E MAC OS    |
		|-----------------------|

		cd osrm-backend

	d.	compile using the following commands:

		|------------|
		|   MAC OS   |
		|------------|

		mkdir build
		
		cd build
		
		cmake ../

		make

		make install

		|--------------|
		|    UBUNTU    |
		|--------------|

		mkdir -p build
		
		cd build

		cmake .. -DCMAKE_BUILD_TYPE=Release
		
		cmake --build .
		
		sudo cmake --build . --target install

		--------------------------------------------------------------------------------------------------------------------------------------------------

		OSRM installation tutorial: https://github.com/Project-OSRM/osrm-backend/wiki/Building-OSRM

		Wiki OSRM Project: https://github.com/Project-OSRM/osrm-backend/wiki

		--------------------------------------------------------------------------------------------------------------------------------------------------

	e.	download italy-latest.osm.pbf from the following website: https://download.geofabrik.de/europe/italy.html

	f.	create an OSRM directory in Documents folder and copy there italy-latest.osm.pbf

	f.	extract the map using the following commands:

		|------------|
		|   MAC OS   |
		|------------|

		osrm-extract italy-latest.osm.pbf -p /usr/local/share/osrm/profiles/car.lua

		(in order to find the directory in which is placed car.lua use the following commands:

			sudo su

			find / -name car.lua

		)

		osrm-partition italy-latest.osrm

		osrm-customize italy-latest.osrm

		|--------------|
		|    UBUNTU    |
		|--------------|

		osrm-extract italy-latest.osm.pbf -p /home/parallels/osrm-backend/profiles/car.lua (la seconda parte della riga di comando deve puntare alla directory in cui è presente il file car.lua)

		osrm-partition italy-latest.osrm

		osrm-customize italy-latest.osrm

3)	CONFIGURE PYTHON 3 VIRTUAL ENVIRONMENT

	a.	use the following commands from terminal:

		pip install virtualenv

		mkdir ~/virtual_envs (choose the desired path for the directory, in my case: ~ is /Development/)
		
		cd ~/virtual_envs
		
		virtualenv -p python3 python3

		--------------------------------------------------------------------------------------------------------------------------------------------------

		Reference: https://stackoverflow.com/questions/54051993/virtualenv-command-not-found-on-mac

		--------------------------------------------------------------------------------------------------------------------------------------------------

	b.	activate python3 virtual environment using the following commands from terminal, after accessing the subfolder "bin"

		source activate

	c.	install libraires using the following commands:

		pip install numpy

		pip install tqdm

		pip install matplotlib

		pip install requests

		pip install aiohttp

		pip install pathlib

	d.	copy osrm-py folder in previously created OSRM folder

	e.	access osrm-py folder and use the following command:

		python setup.py install

	f.	deactivate python3 virtual environment using the following commands from terminal, after accessing the subfolder "bin"

		deactivate

4)	DISTANCES AND DURATIONS MATRICES EVALUATION

	a.	run the OSRM server using the following command (keep it running in background), after accessing the OSRM folder where you previously extracted 	the map

		osrm-routed --algorithm=MLD italy-latest.osrm

		--------------------------------------------------------------------------------------------------------------------------------------------------

		N.B.: in order to verify that the OSRM server is running open a browser and type the following address http://localhost:5000. You should receive the following message “{“code”:”InvalidUrl”,”message”:”URLstring malformed close to position 1: \”\/\””}”

		--------------------------------------------------------------------------------------------------------------------------------------------------

	b.	in a new terminal window, activate python3 virtual env

	c.	after accessing the evaluate_fastest_path project folder, use the following command:

		python evaluate_fastest_paths.py –i <path to input file> -o <path to output folder> (an example is in command_example.sh file)

	d.	the output file will be saved inside "output" folder appending distances and duration matrices

	e.	deactivate python3 virtual environment

	f.	close terminal window where OSRM server is running

		--------------------------------------------------------------------------------------------------------------------------------------------------

		NB: depots are considered in the distances and durations matrix. In case a depot is not present in the problem, put the first coordinate under the #depots tag

		--------------------------------------------------------------------------------------------------------------------------------------------------