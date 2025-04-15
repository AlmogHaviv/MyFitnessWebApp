import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  CardMedia,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Stack,
  Grid,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CloseIcon from '@mui/icons-material/Close';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import { getSimilarUsers, logEvent } from '../../services/api';
import { getSuggestedExercises, Exercise, getSuggestedEquipment } from '../../services/exerciseService';

interface Buddy {
  id_number: number;
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

interface Equipment {
  id: number;
  name: string;
  description: string;
  image: string;
  link: string;
}

const MainPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [buddies, setBuddies] = useState<Buddy[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [animationDirection, setAnimationDirection] = useState<'left' | 'right' | null>(null);
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userDataString = localStorage.getItem('userData');
        if (!userDataString) {
          navigate('/');
          return;
        }

        const parsedUserData = JSON.parse(userDataString);
        setUserData(parsedUserData);

        const similarUsersResponse = await getSimilarUsers(parsedUserData);
        setBuddies(similarUsersResponse.similar_users);

        const fetchedExercises = getSuggestedExercises();
        setExercises(fetchedExercises);

        const fetchedEquipment = getSuggestedEquipment();
        setEquipment(fetchedEquipment);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred while fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const handleLike = async (index: number) => {
    setAnimationDirection('right');

    const currentUser = userData;
    console.log('Current User:', currentUser);

    const likedBuddy = buddies[currentIndex + index];
    console.log('Liked User:', likedBuddy);

    try {
      await logEvent(String(currentUser.id_number), String(likedBuddy.id_number), 'like');
      console.log('Logged event: ', currentUser.full_name, 'Liked', likedBuddy.full_name);
    } catch (error) {
      console.error('Error logging like event:', error);
    }

    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setAnimationDirection(null);
    }, 300);
  };

  const handleDislike = async (index: number) => {
    setAnimationDirection('left');

    const currentUser = userData;
    console.log('Current User:', currentUser);

    const dislikedBuddy = buddies[currentIndex + index];
    console.log('Disliked User:', dislikedBuddy);

    try {
      await logEvent(String(currentUser.id_number), String(dislikedBuddy.id_number), 'dislike');
      console.log('Logged event: ', currentUser.full_name, 'Disliked', dislikedBuddy.full_name);
    } catch (error) {
      console.error('Error logging dislike event:', error);
    }

    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setAnimationDirection(null);
    }, 300);
  };

  if (loading) {
    return (
      <Container
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: '#f9f9f9',
        }}
      >
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">
          {error}
          <Button variant="contained" color="primary" onClick={() => navigate('/')}>
            Go to Registration
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container
      sx={{
        mt: 4,
        backgroundColor: '#f9f9f9',
        borderRadius: '20px',
        boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
        padding: '20px',
      }}
    >
      <Box
        sx={{
          textAlign: 'center',
          mb: 4,
        }}
      >
        <FitnessCenterIcon
          sx={{
            fontSize: '50px',
            color: '#007bff',
            mb: 1,
          }}
        />
        <Typography
          variant="h3"
          sx={{
            fontWeight: 'bold',
            color: '#333',
            mb: 1,
          }}
        >
          Gymder
        </Typography>
        <Typography
          variant="subtitle1"
          sx={{
            color: '#666',
          }}
        >
          Find your perfect workout buddy
        </Typography>
      </Box>

      {/* Suggested Buddies Section */}
      <Box
        sx={{
          boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
          borderRadius: '20px',
          p: 3,
          mb: 4,
          backgroundColor: '#fff',
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: 'bold',
            color: '#333',
            mb: 2,
          }}
        >
          Suggested Buddies
        </Typography>
        {currentIndex < buddies.length ? (
          <Grid container spacing={3}>
            {buddies.slice(currentIndex, currentIndex + 3).map((buddy, index) => (
              <Grid item xs={12} sm={6} md={4} key={buddy.id_number}>
                <Card
                  sx={{
                    borderRadius: '20px',
                    boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
                  }}
                >
                  <CardMedia
                    component="img"
                    height="300"
                    width="300"
                    image={
                      buddy.gender.toLowerCase() === 'female'
                        ? 'https://media.theeverygirl.com/wp-content/uploads/2020/07/little-things-you-can-do-for-a-better-workout-the-everygirl-1.jpg'
                        : 'https://hips.hearstapps.com/hmg-prod/images/young-muscular-build-athlete-exercising-strength-in-royalty-free-image-1706546541.jpg?crop=0.668xw:1.00xh;0.107xw,0&resize=640:*'
                    }
                    alt={buddy.full_name}
                  />
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#333', textAlign: 'center' }}>
                      {buddy.full_name}, {buddy.age}
                    </Typography>
                    <Stack direction="row" justifyContent="center" spacing={2} sx={{ mt: 1 }}>
                      <Typography variant="body2" sx={{ color: '#666' }}>
                        <strong>Height:</strong> {buddy.height} cm
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#666' }}>
                        <strong>Weight:</strong> {buddy.weight} kg
                      </Typography>
                    </Stack>
                    <Stack direction="row" justifyContent="center" spacing={2} sx={{ mt: 1 }}>
                      <Typography variant="body2" sx={{ color: '#666' }}>
                        <strong>VO2 Max:</strong> {buddy.VO2_max}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#666' }}>
                        <strong>Body Fat:</strong> {buddy.body_fat}%
                      </Typography>
                    </Stack>
                    <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 2 }}>
                      <Button
                        variant="contained"
                        color="error"
                        startIcon={<CloseIcon />}
                        onClick={() => handleDislike(index)}
                        sx={{
                          borderRadius: '20px',
                          textTransform: 'none',
                        }}
                      >
                        Dislike
                      </Button>
                      <Button
                        variant="contained"
                        color="success"
                        startIcon={<FavoriteIcon />}
                        onClick={() => handleLike(index)}
                        sx={{
                          borderRadius: '20px',
                          textTransform: 'none',
                        }}
                      >
                        Like
                      </Button>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography variant="body1" sx={{ color: '#666', textAlign: 'center', mt: 2 }}>
            No more matches available. Check back later for new workout buddies!
          </Typography>
        )}
      </Box>

      {/* Suggested Exercises Section */}
      <Box
        sx={{
          boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
          borderRadius: '20px',
          p: 3,
          mb: 4,
          backgroundColor: '#fff',
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: 'bold',
            color: '#333',
            mb: 2,
          }}
        >
          Suggested Exercises
        </Typography>
        <Grid container spacing={3}>
          {exercises.slice(0, 3).map((exercise) => (
            <Grid item xs={12} sm={6} md={4} key={exercise.id}>
              <Card
                sx={{
                  borderRadius: '20px',
                  boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
                }}
              >
                <CardMedia
                  component="iframe"
                  height="200"
                  src={exercise.videoUrl}
                  title={exercise.name}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#333' }}>
                    {exercise.name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    {exercise.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Suggested Fitness Equipment Section */}
      <Box
        sx={{
          boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
          borderRadius: '20px',
          p: 3,
          backgroundColor: '#fff',
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: 'bold',
            color: '#333',
            mb: 2,
          }}
        >
          Suggested Fitness Equipment
        </Typography>
        <Grid container spacing={3}>
          {equipment.slice(0, 3).map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              <Card
                sx={{
                  borderRadius: '20px',
                  boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
                }}
              >
                <CardMedia
                  component="img"
                  height="200"
                  image={item.image}
                  alt={item.name}
                />
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#333' }}>
                    {item.name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#666', mb: 2 }}>
                    {item.description}
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    href={item.link}
                    target="_blank"
                    sx={{
                      borderRadius: '20px',
                      textTransform: 'none',
                    }}
                  >
                    Buy on Amazon
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default MainPage;