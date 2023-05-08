# Installing on Arduino

The Arduino platform is significantly different from the other platforms listed, and as a result, it cannot use the Groundlight SDK directly since it doesn't support standard Python. However, you can still use Groundlight's services with Arduino devices by following an alternative approach.

We have created a dedicated example repository that demonstrates how to use Groundlight with an ESP32-CAM module, which is compatible with Arduino IDE. The repository contains a complete end-to-end example, including integration with the Groundlight services. This example is written in C code and directly calls the Groundlight API by making HTTPS requests.

To get started, please visit the [GitHub repository](https://github.com/groundlight/esp32cam) and follow the instructions provided in the README file. This example will guide you through setting up your Arduino-compatible device to work with Groundlight's services, even though the standard SDK isn't directly applicable to the Arduino platform.

Keep in mind that this example is specifically tailored for the ESP32-CAM module and works well with M5Stack ESP32 Camera, ESP32CAM, and likely others. You may need to verify and update the pinouts for other Arduino-compatible devices. Some hardware devices are more reliable than others, and the software makes regular attempts to reboot as necessary, which often gets things going again.

If you need assistance or have questions about integrating Groundlight with Arduino, please consider opening an issue on the GitHub repository or reaching out to our [support team](mailto:support@groundlight.ai).

## Additional Arduino Resources

To learn more about Arduino and expand your knowledge, you can explore the following resources:

- [Arduino Official Website](https://www.arduino.cc/)
- [Arduino Playground](https://playground.arduino.cc/)
- [Arduino Forum](https://forum.arduino.cc/)
- [ESP32 Community Forum](https://www.esp32.com/)
- [Adafruit Learning System](https://learn.adafruit.com/)

These resources provide extensive documentation, tutorials, and community support for Arduino enthusiasts and developers.

