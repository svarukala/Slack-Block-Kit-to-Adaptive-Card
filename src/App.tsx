import React, { useState } from 'react';
import { Stack,TextField, PrimaryButton, Text } from '@fluentui/react';
import axios from "axios";
import './App.css';


export const App: React.FunctionComponent = () => {

  const [slackJsonInput, setSlackJsonInput] = useState("");
  const [adaptiveCardJsonOutput, setAdaptiveCardJsonOutput] = useState("");

  const handleConvert = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/convert", {
        slackJson: slackJsonInput,
      }, {
        withCredentials: true
      });
      setAdaptiveCardJsonOutput(JSON.stringify(response.data.msTeamsAdaptiveCardJson, null, 2));
    } catch (error) {
      console.error(error);
      alert("An error occurred while converting the JSON. Please try again.");
    }
  };

  return (
    <Stack horizontalAlign="center" verticalAlign="center" verticalFill>
      <Stack style={{ width: "70%" }}>
        <Text variant="xLarge" >Slack Block Kit to Adaptive Card Converter</Text>
        <TextField
          label="Slack Block Kit JSON:"
          multiline
          rows={20}
          value={slackJsonInput}
          onChange={(event, newValue) => setSlackJsonInput(newValue || "")}
        />
        <PrimaryButton className="primary-button" text="Convert to Adaptive Card" onClick={handleConvert} />
        <TextField
          label="Output"
          multiline
          rows={20}
          value={adaptiveCardJsonOutput}
          readOnly
        />
      </Stack>
    </Stack>
  );
};
