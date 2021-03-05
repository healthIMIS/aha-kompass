#!/usr/bin/env python3

# © 2020 Tobias Höpp
# Determine if we are running in production or development setup
import os
production = True
if "PRODUCTION" in os.environ and os.environ["PRODUCTION"] == "true":
    print("Running in production setup.")
else:
    production = False
    print("Running in development setup.")