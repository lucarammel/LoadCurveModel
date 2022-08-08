# Installing a text editor
In order to open and edit various files (python scripts .py, markdown files .md, yaml configuration files .yml, etc), you should install an appropriate text editor, such as Visual Studio Code or Notepad++.


# Installing Python
We want to install python with Anaconda, so you should first install Anaconda.

**Make sure to download the Anaconda x64 version (not x86) as PyTorch won't work on 32-bits python installs, only 64 bits.**

If you are working on a personal computer you should now be able to download and install packages using either conda or pip, however on IEA machines a few more steps are necessary to work with the firewall.

## Making conda installs possible on IEA machines
1. Copy the IEA SSL certificate (CheckPoint SSL Inspection CA (B64 PEM) cert) to user's profile (`C:\Users\<username>\.certificates` as a suggestion), and save it with a .crt extension (e.g. `ieassl.crt`).
2. In an Anaconda Prompt, run this:
    ```
    conda config --set ssl_verify C:\Users\<username>\.certificates\ieassl.crt
    ```
   > Note : You have to specify the full path, not just a relative path to be able to run conda installs from anywhere
3. Open the crt file in VS Code or Notepad++, and copy the entire contents (Ctrl+A, Ctrl+C)
    Append the contents of the .crt file to the following files:
        - `C:\Users\<username>\AppData\Local\Continuum\Anaconda3\Lib\site-packages\certifi\cacert.pem`
        - `C:\Users\<username>\AppData\Local\Continuum\Anaconda3\Library\ssl\cacert.pem`

    You should now be able to run commands such as `conda update conda` successfully.    

4. (optional - if you want to install packages through the graphical interface Anaconda Navigator) Launch Anaconda Navigator, `File -> Preferences`. Add the full path to the .crt file in this dialog

## Making pip installs possible on IEA machines
Nothing to configure, but you need to make sure the `ieassl.crt` file is saved on your computer (in the `C:\Users\<username>\.certificates` folder for instance).
We will need to add the following option to every command we make with pip : `--cert C:\Users\<username>\.certificates\ieassl.crt`


# Setting up the python environment
In an Anaconda Prompt, move to the project folder root.
```
cd /d "R:\BUILDINGS\Modelling\Building Data Repository\ByTheme\Load curves\iea_load_curve_modelling"
```
> The `/d` is required to change directory to another network drive (if you were on the C: drive for instance)
> The quotes are required if there are any spaces in the path (in the names of some folders)

Create a new conda environment and install useful packages (numpy, etc, specified in `environment.yml`), and activate it
```
conda env create -f environment.yml
conda activate iea_load_curve
````
> Note 1 : you will need to activate the environment with the command `conda activate iea_load_curve` every time you want to work with the project (e.g. running the python scripts to train the model or rebuild the dataset, installing new packages with either conda or pip, etc).
>
> You can check that the environment is activated by looking left to the command prompt : it should be `(iea_load_curve)` instead of `(base)`.

> Note 2 : it seems that connectivity errors are frequent on IEA machines, so if you get Connection Failed Errors, it may work by simply trying again.

Install pytorch (the machine learning framework on which our whole model is based), following platform-specific instructions here : https://pytorch.org/get-started/locally/.
```
# On IEA machines, torchvision seems to be blocked by the firewall, but we should not need it anyway
conda install pytorch cpuonly -c pytorch

# On other Windows machines, without GPU acceleration (Cuda)
conda install pytorch torchvision cpuonly -c pytorch

# On macOS
conda install pytorch torchvision -c pytorch
```

On Windows/macOS, install the dependencies for CVXPY optimization library (to be able to do residential/non-residential cooling load separation based on WEO profiles). 
Instructions taken from https://www.cvxpy.org/install/index.html :
- (Windows only) Download the Visual Studio build tools for Python 3 ([download](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16), [install instructions](https://drive.google.com/file/d/0B4GsMXCRaSSIOWpYQkstajlYZ0tPVkNQSElmTWh1dXFaYkJr/view?usp=sharing)). _Note : if you don't find these tools in the Software Center, try contacting the IT Support_
- (macOS only) Install the Xcode command line tools.
You should now be able to install cvxpy using conda
```
conda install -c conda-forge cvxpy
```
> Optional : after installing CVXPY, you can do
> ```
> conda install nose
> nosetests cvxpy
> ```
> to test the installation

> Note : cvxpy can also be installed with pip, but it seems it requires to have numpy and scipy installed with pip too, and not with conda ?

Install remaining packages with pip (as they cannot be installed with conda)
```
pip --cert C:\Users\<username>\.certificates\ieassl.crt install -r requirements.txt
```

> General advices on using conda and pip together (from https://www.anaconda.com/blog/using-pip-in-a-conda-environment):
> - It is best to always use a conda environment different from the (base) one, to avoid messing up the conda installation
> - First install packages you want with conda, then install the ones you want with pip, but you should avoid installing conda packages after installing packages with pip
> - If your environment is messed up (and is not the (base) env), you can always remove/recreate the conda environment
