import React, { useState, useEffect } from "react";
import { Slider, Box, Typography } from "@mui/material";

const PriceSlider = (props) => {
  const { minval, maxval, min, max } = props;

  // Set initial priceRange using minval and maxval from props
  const [priceRange, setPriceRange] = useState([minval, maxval]);

  // Effect to update parent component whenever priceRange changes
  useEffect(() => {
    min(priceRange[0]);
    max(priceRange[1]);
  }, [priceRange]);

  // Sync priceRange state when minval or maxval props change
  useEffect(() => {
    setPriceRange([minval, maxval]);
  }, [minval, maxval]);

  // Handle slider value changes
  const handleChange = (event, newValue) => {
    setPriceRange(newValue); 
  };

  return (
    <Box sx={{ width: 300, margin: "0 auto" }}>
      <Typography variant="h6" gutterBottom>
        Salary Range
      </Typography>
      <Slider
        value={priceRange}
        onChange={handleChange}
        valueLabelDisplay="auto"
        min={0} 
        max={100000} 
        step={100}
      />
      <Typography variant="body1">
        Selected Range: ₹{priceRange[0]} - ₹{priceRange[1]} / month
      </Typography>
    </Box>
  );
};

export default PriceSlider;
