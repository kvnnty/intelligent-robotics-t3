// Arduino sketch to receive serial commands from Python script
// Simulates robot

void setup()
{
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);

  // Set pin 13 (built-in LED) as output
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW); // Start with LED off (robot moving)
}

void loop()
{
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    // Process command
    if (command == '1')
    {
      // Stop the robot (turn on LED)
      digitalWrite(13, HIGH);
      Serial.println("Stopping robot");
    }
    else if (command == '0')
    {
      // Move the robot (turn off LED)
      digitalWrite(13, LOW);
      Serial.println("Moving robot");
    }
  }
}