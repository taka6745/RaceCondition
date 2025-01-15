# RaceCondition

RaceCondition is a custom-styled Tkinter application designed to help test race conditions. It features two main tabs: Mouse Clicker and Key Clicker. Each tab provides unique functionalities to simulate and test race conditions effectively.

## Features

### Mouse Clicker
- **Time Input**: Set a specific time for the mouse click event. The default is the current time, but users can adjust it to a future time.
- **Record Start Position**: Once the user is satisfied with the time input, they can click "Record Start Position". The application will hide and track the mouse's movement.
- **Position Recording**: When the user presses the left shift key, the application records the current mouse position.
- **Countdown and Click**: The application reappears, displaying the recorded X, Y coordinates. A start button initiates a countdown, moving the mouse to the recorded position and clicking at zero.
- **Clock Animation**: Includes a 60-second clock and a 1-second clock (for seconds and milliseconds) to visualize the countdown.
- **Mouse Movement**: The mouse starts at the bottom right of the screen and moves towards the destination, teleporting at the last second to ensure accuracy.

### Key Clicker
- **Keyboard Layout**: Users can select a key from a visual keyboard layout. The selected key turns darker gray.
- **Time Input**: Similar to the Mouse Clicker, users can set a specific time for the key press event.
- **Window Focus**: A dropdown list displays running windows. Users can select a window to focus on when the key press event occurs.
- **Countdown and Key Press**: The application focuses on the selected window and presses the chosen key when the timer hits zero.
- **Clock Animation**: Similar clock animations as the Mouse Clicker to visualize the countdown.

## Installation

To run the RaceCondition application, ensure you have Python and Tkinter installed on your system. Clone the repository and execute the main Python script.

## Usage

1. Launch the application.
2. Navigate to the desired tab (Mouse Clicker or Key Clicker).
3. Configure the settings as per your requirements.
4. Start the test and observe the results.