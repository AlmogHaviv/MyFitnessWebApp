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
import { getSimilarUsers } from '../../services/api';
import { getSuggestedExercises, Exercise, getSuggestedEquipment } from '../../services/exerciseService';

// Define Buddy and Equipment interfaces directly in this file
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userDataString = localStorage.getItem('userData');
        if (!userDataString) {
          navigate('/');
          return;
        }

        const userData = JSON.parse(userDataString);
        const similarUsersResponse = await getSimilarUsers(userData);
        setBuddies(similarUsersResponse.similar_users);

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

  const handleLike = () => {
    console.log('Liked:', buddies[currentIndex]?.full_name);
    setCurrentIndex((prev) => prev + 1);
  };

  const handleDislike = () => {
    console.log('Disliked:', buddies[currentIndex]?.full_name);
    setCurrentIndex((prev) => prev + 1);
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


      {/* Buddy Card or No Matches Message */}
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        {currentIndex < buddies.length ? (
          <Card
            sx={{
              width: '100%',
              maxWidth: 800, // Keep the existing width
              p: 2,
              boxShadow: 5, // Matching shadow
              borderRadius: '15px', // Matching rounded corners
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' }, // Column for mobile, row for larger screens
              alignItems: { xs: 'center', sm: 'stretch' }, // Stretch content on larger screens
              position: 'relative', // Enable absolute positioning for buttons
            }}
          >
            {/* Left: Picture */}
            <CardMedia
              component="img"
              sx={{
                height: { xs: 320, sm: 400 }, // Square for mobile, smaller for larger screens
                width: { xs: 320, sm: 400 }, // Square for mobile, smaller for larger screens
                objectFit: 'cover',
                borderRadius: '15px', // Matching rounded corners
                mb: { xs: 2, sm: 0 }, // Margin bottom for mobile
                mr: { sm: 2 }, // Margin right for larger screens
              }}
              image={
                currentBuddy.gender.toLowerCase() === 'female'
                  ? 'https://media.theeverygirl.com/wp-content/uploads/2020/07/little-things-you-can-do-for-a-better-workout-the-everygirl-1.jpg'
                  : 'https://hips.hearstapps.com/hmg-prod/images/young-muscular-build-athlete-exercising-strength-in-royalty-free-image-1706546541.jpg?crop=0.668xw:1.00xh;0.107xw,0&resize=640:*'
              }
              alt={currentBuddy.full_name}
            />

            {/* Right: Name and Description */}
            <CardContent
              sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center', // Center the content vertically
                alignItems: 'center', // Center the content horizontally
                textAlign: 'center', // Center the text
              }}
            >
              {/* Buddy Info */}
              <Box>
                <Typography variant="h4" gutterBottom>
                  {currentBuddy.full_name}, {currentBuddy.age}
                </Typography>
                <Stack direction="row" spacing={1} justifyContent="center" mb={2}>
                  <Chip label={`VO2 Max: ${currentBuddy.VO2_max}`} color="primary" />
                  <Chip label={`Body Fat: ${currentBuddy.body_fat}%`} />
                </Stack>
                <Typography variant="h6" color="text.secondary" mb={1}>
                  <strong>Height:</strong> {currentBuddy.height} cm
                </Typography>
                <Typography variant="h6" color="text.secondary" mb={2}>
                  <strong>Weight:</strong> {currentBuddy.weight} kg
                </Typography>
              </Box>

              {/* Bottom: Like/Dislike Buttons */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between', // Buttons on opposite edges
                  mt: 2,
                  width: '100%', // Ensure buttons span the full width
                }}
              >
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<CloseIcon />}
                  onClick={handleDislike}
                  sx={{
                    fontSize: '1.2rem',
                    py: 1.5, // Larger button height
                    px: 3, // Larger button width
                    borderRadius: '15px', // Rounded like the card
                    flex: 1, // Make buttons equal width
                    mr: 1, // Add spacing between buttons
                  }}
                >
                  Dislike
                </Button>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<FavoriteIcon />}
                  onClick={handleLike}
                  sx={{
                    fontSize: '1.2rem',
                    py: 1.5, // Larger button height
                    px: 3, // Larger button width
                    borderRadius: '15px', // Rounded like the card
                    flex: 1, // Make buttons equal width
                    ml: 1, // Add spacing between buttons
                  }}
                >
                  Like
                </Button>
              </Box>
            </CardContent>
          </Card>
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
          boxShadow: 5, // Matching shadow
          borderRadius: '15px', // Matching rounded corners
          p: 3, // Padding inside the container
          mx: 'auto', // Center the container horizontally
          mt: 4, // Add margin on top
          backgroundColor: '#fff', // White background for consistency
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
          boxShadow: 5, // Matching shadow
          borderRadius: '15px', // Matching rounded corners
          p: 3, // Padding inside the container
          mx: 'auto', // Center the container horizontally
          mt: 4, // Add margin on top
          backgroundColor: '#fff', // White background for consistency
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
                  borderRadius: '15px', // Matching rounded corners
                  boxShadow: 2, // Subtle shadow for individual cards
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
                      borderRadius: '15px', // Rounded button to match the card
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