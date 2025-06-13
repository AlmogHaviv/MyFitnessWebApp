import React, { useState, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Alert,
  CircularProgress,
} from '@mui/material';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import { createUserProfile, createWorkout } from '../../services/api';
import '../../styles/App.css';

interface UserProfile {
  full_name: string;
  age: number;
  id_number: number;
  gender: string;
  height: number;
  weight: number;
  daily_calories_intake: number;
  resting_heart_rate: number;
  VO2_max: number;
  body_fat: number;
  workout_type: string;
  bmi: number;
  [key: string]: string | number;
}

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<UserProfile>({
    full_name: '',
    age: 0,
    id_number: 0,
    gender: '',
    height: 0,
    weight: 0,
    daily_calories_intake: 0,
    resting_heart_rate: 0,
    VO2_max: 0,
    body_fat: 0,
    workout_type: '',
    bmi: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate all required fields first
      const requiredFields = [
        'full_name',
        'age',
        'id_number',
        'gender',
        'height',
        'weight',
        'daily_calories_intake',
        'resting_heart_rate',
        'VO2_max',
        'body_fat',
        'workout_type'
      ] as const;
      
      for (const field of requiredFields) {
        if (formData[field] === undefined || formData[field] === '') {
          throw new Error(`${field.replace('_', ' ')} is required`);
        }
      }

      // Convert and validate data types
      const heightM = Number(formData.height) / 100;
      const bmi = Number(formData.weight) / (heightM * heightM);

      const userProfileData = {
        full_name: formData.full_name.trim(),
        age: Math.floor(Number(formData.age)),
        id_number: Math.floor(Number(formData.id_number)),
        gender: formData.gender,
        height: Math.floor(Number(formData.height)),
        weight: Math.floor(Number(formData.weight)),
        daily_calories_intake: Math.floor(Number(formData.daily_calories_intake)),
        resting_heart_rate: Math.floor(Number(formData.resting_heart_rate)),
        VO2_max: Number(formData.VO2_max),
        body_fat: Number(formData.body_fat),
        bmi: Number(bmi.toFixed(1)), 
      };

      // Update gender validation to match MenuItem values
      if (!['Male', 'Female', 'Other'].includes(userProfileData.gender)) {
        throw new Error('Invalid gender value');
      }

      // Update workout type validation to match MenuItem values
      if (!['Cycling', 'Cardio', 'HIIT', 'Strength', 'Yoga', 'Running'].includes(formData.workout_type)) {
        throw new Error('Invalid workout type value');
      }

      console.log('Submitting user profile:', userProfileData);
      console.log('Submitting workout type:', formData.workout_type);

      // First create the user profile
      const userResponse = await createUserProfile(userProfileData);
      console.log('User created:', userResponse);
      
      // Then create the workout preference
      const workoutData = {
        id_number: userProfileData.id_number,
        workout_type: formData.workout_type
      };
      const workoutResponse = await createWorkout(workoutData);
      console.log('Workout created:', workoutResponse);
      
      // Store user data in localStorage
      localStorage.setItem('userData', JSON.stringify({...userProfileData, workout_type: formData.workout_type}));
      
      // Navigate to main page
      navigate('/main');
    } catch (err) {
      console.error('Submission error:', err); // Debug log
      setError(err instanceof Error ? err.message : 'An error occurred while creating your profile');
    } finally {
      setLoading(false);
    }
  };

  const handleTextChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'full_name' ? value : Number(value)
    }));
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Container className="landing-container">
      <Box className="landing-header">
        <FitnessCenterIcon className="landing-icon" />
        <Typography className="landing-title">
          Welcome to Gymder
        </Typography>
        <Typography className="landing-subtitle">
          Find your perfect workout buddy
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" className="error-container">
          {error}
        </Alert>
      )}

      <Paper
        className="form-container"
        elevation={3}
        sx={{
          boxShadow: 5, // Matching shadow
          borderRadius: '15px', // Matching rounded corners
          p: 3, // Padding inside the card
          mx: 'auto', // Center the card horizontally
          maxWidth: 800, // Match the width of the Main Page card
          backgroundColor: '#fff', // White background for consistency
        }}
      >
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3} className="form-grid">
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                name="full_name"
                value={formData.full_name}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Age"
                name="age"
                type="number"
                value={formData.age || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="ID Number"
                name="id_number"
                type="number"
                value={formData.id_number || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Gender</InputLabel>
                <Select
                  name="gender"
                  value={formData.gender}
                  onChange={handleSelectChange}
                  required
                >
                  <MenuItem value="Male">Male</MenuItem>
                  <MenuItem value="Female">Female</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Workout Type</InputLabel>
                <Select
                  name="workout_type"
                  value={formData.workout_type}
                  onChange={handleSelectChange}
                  required
                >
                  <MenuItem value="Cycling">Cycling</MenuItem>
                  <MenuItem value="Cardio">Cardio</MenuItem>
                  <MenuItem value="HIIT">HIIT</MenuItem>
                  <MenuItem value="Strength">Strength</MenuItem>
                  <MenuItem value="Yoga">Yoga</MenuItem>
                  <MenuItem value="Running">Running</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Height (cm)"
                name="height"
                type="number"
                value={formData.height || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Weight (kg)"
                name="weight"
                type="number"
                value={formData.weight || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Daily Calories Intake"
                name="daily_calories_intake"
                type="number"
                value={formData.daily_calories_intake || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Resting Heart Rate (bpm)"
                name="resting_heart_rate"
                type="number"
                value={formData.resting_heart_rate || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="VO2 Max"
                name="VO2_max"
                type="number"
                value={formData.VO2_max || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Body Fat %"
                name="body_fat"
                type="number"
                value={formData.body_fat || ''}
                onChange={handleTextChange}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading}
                sx={{
                  borderRadius: '15px', // Rounded button to match the card
                }}
              >
                {loading ? <CircularProgress size={24} /> : ' Register and Find My Workout Buddy'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default LandingPage;