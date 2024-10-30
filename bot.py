# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F401
from collections.abc import Callable

import numpy as np

from vendeeglobe import (
    Checkpoint,
    Heading,
    Instructions,
    Location,
    Vector,
    config,
)
from vendeeglobe.utils import distance_on_surface


class Bot:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = "TeamName"  # This is your team name
        # This is the course that the ship has to follow
        self.course = [
             Checkpoint(latitude=43.797109, longitude=-11.264905, radius=50),
            Checkpoint(longitude=-57.16281, latitude=16.79314, radius=50),
            Checkpoint(longitude=-60.86658, latitude=14.33136, radius=10),
            Checkpoint(longitude=-75.99475, latitude=14.88418, radius=50),
            Checkpoint(longitude=-80.25195, latitude=10.05314, radius=30),
            Checkpoint(longitude=-79.91893, latitude=9.34789, radius=10),
            Checkpoint(longitude=-79.47879, latitude=8.92079, radius=10),
            Checkpoint(longitude=-79.21698, latitude=6.81393, radius=30),
            Checkpoint(longitude=-150.0, latitude=3, radius=100),
            Checkpoint(longitude=132.97296,latitude=2.67776,radius=50),
            Checkpoint(longitude=129.74323,latitude=-2.44015,radius=10),
            Checkpoint(longitude=125.12873,latitude=-2.96691,radius=10),
            Checkpoint(longitude=128.47406, latitude=-8.21340, radius=50),
            Checkpoint(longitude=128.54547,latitude=-11.34191,radius=10),
            Checkpoint(longitude=115.78259, latitude=-14.16543, radius=50),
            Checkpoint(longitude=70, latitude=-20, radius=50),
            Checkpoint(longitude=22.09, latitude=-36.693, radius=50),
            Checkpoint(longitude=12, latitude=-36.9, radius=50),
            Checkpoint(longitude=-24.97424, latitude=14.06509, radius=50),
            Checkpoint(longitude=-11.13147, latitude=45.53168, radius=50),
            Checkpoint(
                latitude=config.start.latitude,
                longitude=config.start.longitude,
                radius=5,
            ),
        ]

    def run(
        self,
        t: float,
        dt: float,
        longitude: float,
        latitude: float,
        heading: float,
        speed: float,
        vector: np.ndarray,
        forecast: Callable,
        world_map: Callable,
    ) -> Instructions:
        """
        This is the method that will be called at every time step to get the
        instructions for the ship.

        Parameters
        ----------
        t:
            The current time in hours.
        dt:
            The time step in hours.
        longitude:
            The current longitude of the ship.
        latitude:
            The current latitude of the ship.
        heading:
            The current heading of the ship.
        speed:
            The current speed of the ship.
        vector:
            The current heading of the ship, expressed as a vector.
        forecast:
            Method to query the weather forecast for the next 5 days.
            Example:
            current_position_forecast = forecast(
                latitudes=latitude, longitudes=longitude, times=0
            )
        world_map:
            Method to query map of the world: 1 for sea, 0 for land.
            Example:
            current_position_terrain = world_map(
                latitudes=latitude, longitudes=longitude
            )

        Returns
        -------
        instructions:
            A set of instructions for the ship. This can be:
            - a Location to go to
            - a Heading to point to
            - a Vector to follow
            - a number of degrees to turn Left
            - a number of degrees to turn Right

            Optionally, a sail value between 0 and 1 can be set.
        """
        # Initialize the instructions
        instructions = Instructions()

        # TODO: Remove this, it's only for testing =================
        current_position_forecast = forecast(
            latitudes=latitude, longitudes=longitude, times=0
        )
        current_position_terrain = world_map(latitudes=latitude, longitudes=longitude)
        # ===========================================================

        # Go through all checkpoints and find the next one to reach
        for ch in self.course:
            # Compute the distance to the checkpoint
            dist = distance_on_surface(
                longitude1=longitude,
                latitude1=latitude,
                longitude2=ch.longitude,
                latitude2=ch.latitude,
            )
            # Consider slowing down if the checkpoint is close
            jump = dt * np.linalg.norm(speed)
            if dist < 2.0 * ch.radius + jump:
                instructions.sail = min(ch.radius / jump, 1)
            else:
                instructions.sail = 1.0
            # Check if the checkpoint has been reached
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                instructions.location = Location(
                    longitude=ch.longitude, latitude=ch.latitude
                )
                break

        return instructions
