# cloud-simulator

## Installation Guide

We validated this guide in Ubuntu Desktop 20.04.1 LTS (5.4.0-45-generic x86_64 GNU/Linux). It is worth noting some commands below require a user account with sudo administrator privileges.

Modern Linux distributions come with Python3 by default. So, to check out if we already have it, we can run the following command in our console terminal:
```{bash}
python3 -V
```

In case we don't have Python3 yet, let's install it (we recommend using Python 3.6 or superior). In Linux distributions with support to the "apt" package manager, we can easily install Python3 running the following commands:

```{bash}
# Updates and refreshes repository lists
sudo apt update

# Installs supporting software
sudo apt install -y software-properties-common

# Adds Deadsnakes PPA to the repositories list (this make it easier to get newer releases)
sudo add-apt-repository ppa:deadsnakes/ppa

# Adds git-core PPA that allows to download git
sudo add-apt-repository ppa:git-core/ppa

# Updates the repository lists once again
sudo apt update

# Installs git
sudo apt install -y git-core

# Installs Python 3.8
sudo apt install python3.8 python3.8-dev

# Check out the Python installation
python3 -V

# Installs graphviz Linux package and other dependencies
sudo apt install graphviz libgraphviz-dev pkg-config
```

Once we have Python installed, we need to get pip3, a tool that allows us to install and manage Python packages. To do that, we run the following command:

```{bash}
sudo apt install -y python3-pip
```

Once we have installed all dependencies, we can get the simulator from GitHub:
```{bash}
# Cloning the repository
git clone https://github.com/GRIN-PUCRS/edge-simulator.git

# Entering the simulator's directory
cd edge-simulator/
```

Before starting using the edge-simulator, the last step consists of installing all Python dependencies the project uses to deliver its functionality. We can quickly get them all through the `requirements.txt` file:

```{bash}
pip3 install -r requirements.txt
```

## Using the Simulator

To use the simulator, we just need to call main.py, passing some required arguments. Usually, we need to specify the following arguments:

- **Simulation type:** tells which type of simulation we want to run, either 'normal' or 'real_time'. If we use the 'normal' option, the simulator walks through time steps as fast as possible. Conversely, using 'real_time' tells the simulator to walk through time steps based on wall-clock time. We inform a valid simulation type value (either 'normal' or 'real_time') using `--simulation-type` or `-s`.
- **Dataset:** defines the input file used to create the simulation environment. Valid dataset values correspond to JSON file names in 'data' directory. We omit the '.json' extension while passing this option to the simulator. We inform the simulator which dataset we want to run using `--dataset` or `-d`.
- **Maintenance Strategy:** informs the simulator which maintenance strategy we want to execute. Before calling a maintenance strategy, we need to ensure it is imported in 'simulator.py', pointing to a valid file in 'simulator/components/resource_management/maintenance'. We assign a maintenance strategy using `--maintenance-strategy` or `-m`.
- **Output:** tells the simulator the name of a file it must create to store the simulation output. By default, the simulator creates an Excel spreadsheet file (using the 'xlsx' extension) with worksheets containing both 'overall' and 'by step' metrics. We define an output file using `--output-file` or `-o`.

Specifying the arguments above, we can simulate multiple maintenance scenarios as shown below:

```{bash}
python3 -B -m simulator -s="normal" -d="dataset25occupation" -m="first_fit_like" -o="first_fit_like_50occupation"
python3 -B -m simulator -s="normal" -d="dataset25occupation" -m="worst_fit_like" -o="worst_fit_like_50occupation"
python3 -B -m simulator -s="normal" -d="dataset25occupation" -m="best_fit_like" -o="best_fit_like_50occupation"
python3 -B -m simulator -s="normal" -d="dataset25occupation" -m="salus" -o="salus_50occupation"

python3 -B -m simulator -s="normal" -d="dataset50occupation" -m="first_fit_like" -o="first_fit_like_25occupation"
python3 -B -m simulator -s="normal" -d="dataset50occupation" -m="worst_fit_like" -o="worst_fit_like_25occupation"
python3 -B -m simulator -s="normal" -d="dataset50occupation" -m="best_fit_like" -o="best_fit_like_25occupation"
python3 -B -m simulator -s="normal" -d="dataset50occupation" -m="salus" -o="salus_25occupation"

python3 -B -m simulator -s="normal" -d="dataset75occupation" -m="first_fit_like" -o="first_fit_like_75occupation"
python3 -B -m simulator -s="normal" -d="dataset75occupation" -m="worst_fit_like" -o="worst_fit_like_75occupation"
python3 -B -m simulator -s="normal" -d="dataset75occupation" -m="best_fit_like" -o="best_fit_like_75occupation"
python3 -B -m simulator -s="normal" -d="dataset75occupation" -m="salus" -o="salus_75occupation"
```
