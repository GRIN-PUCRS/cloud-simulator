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
```

Once we have Python installed, we need to get pip3, a tool that allows us to install and manage Python packages. To do that, we run the following command:

```{bash}
sudo apt install -y python3-pip
```

Once we have installed all dependencies, we can get the simulator from GitHub:
```{bash}
# Cloning the repository
git clone https://github.com/GRIN-PUCRS/cloud-simulator.git

# Entering the simulator's directory
cd cloud-simulator/
```

Before starting using the cloud-simulator, the last step consists of installing all Python dependencies the project uses to deliver its functionality. We can quickly get them all through the `requirements.txt` file:

```{bash}
pip3 install -r requirements.txt
```

## Using the Simulator

To run the simulator, we can execute the following command from the simulator's root directory:

```{bash}
python3 -B -m simulator
```

To test different scenarios, we can modify the `main.py` file, choosing different input files (dataset = 'data/YOUR_INPUT_DATA.json') or different strategies (env.process(YOUR_STRATEGY(env, maintenance_data))).


### TO-DO LIST

- [ ] Adopt a code linter (standardized code within multiple collaborators)
- [ ] Expand the LICENSE.md file
- [ ] Implement tests
- [ ] Implement exceptions
- [ ] Implement examples
- [ ] Populate the README.md files (suggestions below)
    - Root: Introduction (Motivation and Goals), Arquitecture, Project Structure, Team, etc.
    - simulator/: Summary (files in this level), Minimal example
    - components/: In-depth explanation of the arquitecture
    - components/[component_name]: In-depth explanation of the module and its components
