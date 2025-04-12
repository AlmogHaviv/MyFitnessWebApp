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
import { createUserProfile } from '../../services/api';
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
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate form data
      if (!formData.full_name || !formData.id_number || !formData.gender) {
        throw new Error('Please fill in all required fields');
      }

      // Send data to backend
      const response = await createUserProfile(formData);
      
      // Store user ID in localStorage for future use
      localStorage.setItem('userId', response.id_number.toString());
      
      // Navigate to main page
      navigate('/main');
    } catch (err) {
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

      <Paper className="form-container" elevation={3}>
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
                  <MenuItem value="male">Male</MenuItem>
                  <MenuItem value="female">Female</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
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
              >
                {loading ? <CircularProgress size={24} /> : 'Find My Workout Buddy'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default LandingPage; 