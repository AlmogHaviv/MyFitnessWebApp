import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Grid,
  IconButton,
  Chip,
  Container,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CloseIcon from '@mui/icons-material/Close';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import { getSimilarUsers, getWorkoutRecommendations } from '../../services/api';
import '../../styles/App.css';

interface Buddy {
  id: number;
  full_name: string;
  age: number;
  gender: string;
  height: number;
  weight: number;
  daily_calories_intake: number;
  resting_heart_rate: number;
  VO2_max: number;
  body_fat: number;
}

interface WorkoutRecommendation {
  workout_type: string;
  workout_intensity: string;
  duration: number;
  confidence_score: number;
}

const MainPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [buddies, setBuddies] = useState<Buddy[]>([]);
  const [recommendations, setRecommendations] = useState<WorkoutRecommendation[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userId = localStorage.getItem('userId');
        if (!userId) {
          // If no user ID is found, redirect to landing page
          navigate('/');
          return;
        }

        // Fetch similar users and recommendations
        const [similarUsers, workoutRecommendations] = await Promise.all([
          getSimilarUsers(Number(userId)),
          getWorkoutRecommendations(Number(userId))
        ]);

        setBuddies(similarUsers.similar_users);
        setRecommendations(workoutRecommendations.recommended_workouts);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred while fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const handleLike = async () => {
    // Here you would typically send the like to your backend
    console.log('Liked:', buddies[currentIndex].full_name);
    setCurrentIndex(prev => prev + 1);
  };

  const handleDislike = async () => {
    // Here you would typically send the dislike to your backend
    console.log('Disliked:', buddies[currentIndex].full_name);
    setCurrentIndex(prev => prev + 1);
  };

  if (loading) {
    return (
      <Container className="loading-container">
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="error-container">
        <Alert severity="error">
          {error}
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => navigate('/')}
          >
            Go to Registration
          </Button>
        </Alert>
      </Container>
    );
  }

  if (currentIndex >= buddies.length) {
    return (
      <Container className="main-container">
        <Box className="no-matches">
          <Typography variant="h5" gutterBottom>
            No more matches right now
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Check back later for new workout buddies!
          </Typography>
        </Box>
      </Container>
    );
  }

  const currentBuddy = buddies[currentIndex];

  return (
    <Container className="main-container">
      <Box className="workout-recommendations">
        <Typography variant="h6" gutterBottom>
          Your Workout Recommendations
        </Typography>
        <Grid container spacing={2}>
          {recommendations.map((rec, index) => (
            <Grid item xs={12} key={index}>
              <Card className="recommendation-card">
                <CardContent>
                  <Typography variant="h6">{rec.workout_type}</Typography>
                  <Typography color="text.secondary">
                    Intensity: {rec.workout_intensity}
                  </Typography>
                  <Typography color="text.secondary">
                    Duration: {rec.duration} minutes
                  </Typography>
                  <Typography color="text.secondary">
                    Confidence: {(rec.confidence_score * 100).toFixed(1)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Typography variant="h6" gutterBottom>
        Potential Workout Buddies
      </Typography>
      <Card className="buddy-card">
        <CardMedia
          className="buddy-image"
          component="img"
          image={`https://source.unsplash.com/random/300x300/?fitness,${currentBuddy.gender}`}
          alt={currentBuddy.full_name}
        />
        <CardContent className="buddy-info">
          <Typography className="buddy-name">
            {currentBuddy.full_name}, {currentBuddy.age}
          </Typography>
          
          <Box className="buddy-stats">
            <Chip
              icon={<FitnessCenterIcon />}
              label={`VO2 Max: ${currentBuddy.VO2_max}`}
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`Body Fat: ${currentBuddy.body_fat}%`}
              variant="outlined"
            />
          </Box>

          <Typography className="buddy-details">
            <strong>Height:</strong> {currentBuddy.height} cm
          </Typography>
          <Typography className="buddy-details">
            <strong>Weight:</strong> {currentBuddy.weight} kg
          </Typography>

          <Box className="action-buttons">
            <Button
              className="action-button like-button"
              startIcon={<FavoriteIcon />}
              onClick={handleLike}
            >
              Like
            </Button>
            <Button
              className="action-button dislike-button"
              startIcon={<CloseIcon />}
              onClick={handleDislike}
            >
              Dislike
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default MainPage; 