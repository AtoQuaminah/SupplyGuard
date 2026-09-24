"""Build metadata placeholder for install_risk_pkg."""

import os
import subprocess

def configure():
    os.system('echo setup step')
    return 'configured'
