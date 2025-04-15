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

// Define Buddy and Equipment interfaces directly in this file
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
  const [userData, setUserData] = useState<any>(null); // Add userData state

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userDataString = localStorage.getItem('userData');
        if (!userDataString) {
          navigate('/');
          return;
        }

        const parsedUserData = JSON.parse(userDataString);
        setUserData(parsedUserData); // Store userData in state

        const similarUsersResponse = await getSimilarUsers(parsedUserData);
        setBuddies(similarUsersResponse.similar_users);
        // console.log('Similar Users:', similarUsersResponse.similar_users);

        // Fetch suggested exercises
        const fetchedExercises = getSuggestedExercises();
        setExercises(fetchedExercises);

        // Fetch suggested equipment from the service
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

    setAnimationDirection('right'); // Slide out to the right

    const currentUser = userData;
    console.log('Current User:', currentUser);

    const likedBuddy = buddies[currentIndex + index];
    console.log('Liked User:', likedBuddy);


    try {
      // Log the like event
      await logEvent(String(currentUser.id_number), String(likedBuddy.id_number), 'like');
      console.log('Logged event: ',currentUser.full_name,'Liked', likedBuddy.full_name);
    } catch (error) {
      console.error('Error logging like event:', error);
    }

    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setAnimationDirection(null); // Reset animation
    }, 300); // Match the animation duration
  };

  const handleDislike = async (index: number) => {

    setAnimationDirection('left'); // Slide out to the right

    const currentUser = userData;
    console.log('Current User:', currentUser);

    const dislikedBuddy = buddies[currentIndex + index];
    console.log('Disiked User:', dislikedBuddy);


    try {
      // Log the like event
      await logEvent(String(currentUser.id_number), String(dislikedBuddy.id_number), 'dislike');
      console.log('Logged event: ',currentUser.full_name,'Disiked', dislikedBuddy.full_name);
    } catch (error) {
      console.error('Error logging like event:', error);
    }

    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setAnimationDirection(null); // Reset animation
    }, 300); // Match the animation duration
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
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

  const currentBuddy = buddies[currentIndex];

  return (
    <Container sx={{ mt: 4 }}>
      <Box className="landing-header">
        <FitnessCenterIcon className="landing-icon" />
        <Typography className="landing-title">
          Gymder
        </Typography>
        <Typography className="landing-subtitle">
          Find your perfect workout buddy
        </Typography>
      </Box>

      {/* Buddy Cards or No Matches Message */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '50vh',
          flexDirection: 'column',
        }}
      >
        {currentIndex < buddies.length ? (
          <Grid
            container
            spacing={3}
            justifyContent="center" // Center the cards horizontally
            alignItems="center" // Center the cards vertically
            sx={{
              maxWidth: 1200, // Match the width of the Suggested Exercises section
              mx: 'auto', // Center the grid horizontally
            }}
          >
            {buddies.slice(currentIndex, currentIndex + 3).map((buddy, index) => (
              <Grid item xs={12} sm={6} md={4} key={buddy.id_number}>
                <Card
                  sx={{
                    width: '100%',
                    maxWidth: 300, // Reduce the card width
                    p: 2,
                    boxShadow: 5,
                    borderRadius: '15px',
                    display: 'flex',
                    flexDirection: 'column', // Stack content vertically
                    alignItems: 'center', // Center content horizontally
                    position: 'relative',
                  }}
                >
                  {/* Picture */}
                  <CardMedia
                    component="img"
                    sx={{
                      height: 300, // Reduce image height to make the card shorter
                      width: '100%',
                      objectFit: 'cover',
                      borderRadius: '15px',
                      mb: 2,
                    }}
                    image={
                      buddy.gender.toLowerCase() === 'female'
                        ? 'https://media.theeverygirl.com/wp-content/uploads/2020/07/little-things-you-can-do-for-a-better-workout-the-everygirl-1.jpg'
                        : 'https://hips.hearstapps.com/hmg-prod/images/young-muscular-build-athlete-exercising-strength-in-royalty-free-image-1706546541.jpg?crop=0.668xw:1.00xh;0.107xw,0&resize=640:*'
                    }
                    alt={buddy.full_name}
                  />

                  {/* Name and Description */}
                  <CardContent
                    sx={{
                      flex: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      textAlign: 'center',
                      p: 1, // Reduce padding inside the card
                    }}
                  >
                    <Typography variant="h6" gutterBottom>
                      {buddy.full_name}, {buddy.age}
                    </Typography>
                    <Stack direction="row" spacing={1} justifyContent="center" mb={1}>
                      <Chip label={`VO2 Max: ${buddy.VO2_max}`} color="primary" />
                      <Chip label={`Body Fat: ${buddy.body_fat}%`} />
                    </Stack>
                    <Typography variant="body2" color="text.secondary" mb={1}>
                      <strong>Height:</strong> {buddy.height} cm
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Weight:</strong> {buddy.weight} kg
                    </Typography>
                  </CardContent>

                  {/* Like/Dislike Buttons */}
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      mt: 1, // Reduce margin above buttons
                      width: '100%',
                    }}
                  >
                    <Button
                      variant="contained"
                      color="error"
                      startIcon={<CloseIcon />}
                      onClick={() => handleDislike(index)}
                      sx={{
                        fontSize: '0.9rem', // Smaller font size
                        py: 1, // Reduce button height
                        px: 2, // Reduce button width
                        borderRadius: '15px',
                        flex: 1,
                        mr: 1,
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
                        fontSize: '0.9rem', // Smaller font size
                        py: 1, // Reduce button height
                        px: 2, // Reduce button width
                        borderRadius: '15px',
                        flex: 1,
                        ml: 1,
                      }}
                    >
                      Like
                    </Button>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Card sx={{ width: '100%', maxWidth: 500, boxShadow: 5, textAlign: 'center', p: 0, borderRadius: '15px' }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="h5" gutterBottom>
                No more matches right now
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Check back later for new workout buddies!
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>

      {/* Suggested Exercises Section */}
      <Box
        sx={{
          boxShadow: 5,
          borderRadius: '15px',
          p: 3,
          mx: 'auto',
          mt: 4,
          backgroundColor: '#fff',
        }}
      >
        <Typography variant="h4" className="section-title" gutterBottom>
          Suggested Exercises
        </Typography>
        <Grid container spacing={2} justifyContent="center">
          {exercises.slice(0, 3).map((exercise) => (
            <Grid item xs={12} sm={6} md={4} key={exercise.id}>
              <Card
                sx={{
                  width: '100%',
                  borderRadius: '15px',
                  boxShadow: 2,
                }}
              >
                <CardMedia
                  component="iframe"
                  height="300"
                  src={exercise.videoUrl}
                  title={exercise.name}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {exercise.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
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
          boxShadow: 5,
          borderRadius: '15px',
          p: 3,
          mx: 'auto',
          mt: 4,
          backgroundColor: '#fff',
        }}
      >
        <Typography variant="h4" className="section-title" gutterBottom>
          Suggested Fitness Equipment
        </Typography>
        <Grid container spacing={2} justifyContent="center">
          {equipment.slice(0, 3).map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              <Card
                sx={{
                  width: '100%',
                  borderRadius: '15px',
                  boxShadow: 2,
                }}
              >
                <CardMedia
                  component="img"
                  height="300"
                  image={item.image}
                  alt={item.name}
                />
                <CardContent>
                  <Typography variant="h6">{item.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.description}
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    href={item.link}
                    target="_blank"
                    sx={{
                      mt: 2,
                      borderRadius: '15px',
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