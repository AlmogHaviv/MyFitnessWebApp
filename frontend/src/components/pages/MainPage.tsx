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
import Slide from '@mui/material/Slide';
import Fade from '@mui/material/Fade';
import MaleIcon from '@mui/icons-material/Male';
import FemaleIcon from '@mui/icons-material/Female';
import { getSimilarUsers, recommendBuddies, logEvent } from '../../services/api';
import { getSuggestedExercises, Exercise, getSuggestedEquipment } from '../../services/exerciseService';
import { getRandomImageByGender } from '../../services/imageStock';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

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
  workout_type: string;
  distance: number; // Added distance property for sorting
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

  // States for "Similar Buddies"
  const [buddies, setBuddies] = useState<Buddy[]>([]);
  const [currentBuddies, setCurrentBuddies] = useState<Buddy[]>([]);
  const [seenBuddies, setSeenBuddies] = useState<Set<number>>(new Set());

  // States for "Recommended Buddies"
  const [recommendedBuddies, setRecommendedBuddies] = useState<Buddy[]>([]);
  const [currentRecommendedBuddies, setCurrentRecommendedBuddies] = useState<Buddy[]>([]);
  const [seenRecommendedBuddies, setSeenRecommendedBuddies] = useState<Set<number>>(new Set());

  // States for Exercises and Equipment
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);

  const [userData, setUserData] = useState<any>(null);
  const [animationDirection, setAnimationDirection] = useState<'left' | 'right' | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

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

        // Fetch similar buddies
        const similarUsersResponse = await getSimilarUsers(parsedUserData);
        const sortedBuddies = similarUsersResponse.similar_users.sort(
          (a: Buddy, b: Buddy) => a.distance - b.distance
        );
        setBuddies(sortedBuddies);
        setCurrentBuddies(sortedBuddies.slice(0, 3));
        setSeenBuddies(new Set(sortedBuddies.slice(0, 3).map((buddy: { id_number: any; }) => buddy.id_number)));

        // Fetch recommended buddies
        const recommendations = await recommendBuddies(String(parsedUserData.id_number));
        setRecommendedBuddies(recommendations.recommended_buddies);
        setCurrentRecommendedBuddies(recommendations.recommended_buddies.slice(0, 3));
        setSeenRecommendedBuddies(
          new Set(recommendations.recommended_buddies.slice(0, 3).map((buddy: { id_number: any; }) => buddy.id_number))
        );


        // Fetch suggested exercises and equipment
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

  const replaceBuddy = (index: number) => {
    const updatedSeenBuddies = new Set(seenBuddies);
    const currentBuddy = currentBuddies[index];
    updatedSeenBuddies.add(currentBuddy.id_number); // Mark the current buddy as seen

    // Find the next unseen buddy
    const nextBuddy = buddies.find((buddy) => !updatedSeenBuddies.has(buddy.id_number));

    if (nextBuddy) {
      const updatedCurrentBuddies = [...currentBuddies];
      updatedCurrentBuddies[index] = nextBuddy; // Replace the current buddy with the next unseen buddy
      setAnimationDirection('left'); // Trigger the animation
      setTimeout(() => {
        setCurrentBuddies(updatedCurrentBuddies);
        updatedSeenBuddies.add(nextBuddy.id_number); // Mark the new buddy as seen
        setAnimationDirection(null); // Reset animation
      }, 300); // Match the animation duration
    } else {
      // If no unseen buddies are left, remove the current buddy
      const updatedCurrentBuddies = [...currentBuddies];
      updatedCurrentBuddies.splice(index, 1);
      setAnimationDirection('left'); // Trigger the animation
      setTimeout(() => {
        setCurrentBuddies(updatedCurrentBuddies);
        setAnimationDirection(null); // Reset animation
      }, 300); // Match the animation duration
    }

    setSeenBuddies(updatedSeenBuddies);
  };

  const replaceRecommendedBuddy = (index: number) => {
    const updatedSeenRecommendedBuddies = new Set(seenRecommendedBuddies);
    const currentBuddy = currentRecommendedBuddies[index];
    updatedSeenRecommendedBuddies.add(currentBuddy.id_number);

    const nextBuddy = recommendedBuddies.find(
      (buddy) => !updatedSeenRecommendedBuddies.has(buddy.id_number)
    );

    if (nextBuddy) {
      const updatedCurrentRecommendedBuddies = [...currentRecommendedBuddies];
      updatedCurrentRecommendedBuddies[index] = nextBuddy;
      setCurrentRecommendedBuddies(updatedCurrentRecommendedBuddies);
      updatedSeenRecommendedBuddies.add(nextBuddy.id_number);
    } else {
      const updatedCurrentRecommendedBuddies = [...currentRecommendedBuddies];
      updatedCurrentRecommendedBuddies.splice(index, 1);
      setCurrentRecommendedBuddies(updatedCurrentRecommendedBuddies);
    }

    setSeenRecommendedBuddies(updatedSeenRecommendedBuddies);
  };

  const handleLike = async (index: number) => {
    setAnimationDirection('right');

    const currentUser = userData;
    const likedBuddy = currentBuddies[index];
    console.log('Liked User:', likedBuddy);

    try {
      await logEvent(String(currentUser.id_number), String(likedBuddy.id_number), 'like');
      console.log('Logged event: ', currentUser.full_name, 'Liked', likedBuddy.full_name);
    } catch (error) {
      console.error('Error logging like event:', error);
    }

    setTimeout(() => {
      replaceBuddy(index); // Replace the liked buddy
      setAnimationDirection(null);
    }, 300);
  };

  const handleDislike = async (index: number) => {
    setAnimationDirection('left');

    const currentUser = userData;
    const dislikedBuddy = currentBuddies[index];
    console.log('Disliked User:', dislikedBuddy);

    try {
      await logEvent(String(currentUser.id_number), String(dislikedBuddy.id_number), 'dislike');
      console.log('Logged event: ', currentUser.full_name, 'Disliked', dislikedBuddy.full_name);
    } catch (error) {
      console.error('Error logging dislike event:', error);
    }

    setTimeout(() => {
      replaceBuddy(index); // Replace the disliked buddy
      setAnimationDirection(null);
    }, 300);
  };

  const handleLikeRecommended = async (index: number) => {
    setAnimationDirection('right');

    const currentUser = userData;
    const likedBuddy = currentRecommendedBuddies[index];
    console.log('Liked Recommended User:', likedBuddy);

    try {
      await logEvent(String(currentUser.id_number), String(likedBuddy.id_number), 'like');
      console.log('Logged event: ', currentUser.full_name, 'Liked Recommended', likedBuddy.full_name);
    } catch (error) {
      console.error('Error logging like event for recommended buddy:', error);
    }

    setTimeout(() => {
      replaceRecommendedBuddy(index); // Replace the liked recommended buddy
      setAnimationDirection(null);
    }, 300);
  };

  const handleDislikeRecommended = async (index: number) => {
    setAnimationDirection('left');

    const currentUser = userData;
    const dislikedBuddy = currentRecommendedBuddies[index];
    console.log('Disliked Recommended User:', dislikedBuddy);

    try {
      await logEvent(String(currentUser.id_number), String(dislikedBuddy.id_number), 'dislike');
      console.log('Logged event: ', currentUser.full_name, 'Disliked Recommended', dislikedBuddy.full_name);
    } catch (error) {
      console.error('Error logging dislike event for recommended buddy:', error);
    }

    setTimeout(() => {
      replaceRecommendedBuddy(index); // Replace the disliked recommended buddy
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
        position: 'relative', // Ensure positioning for the logout button and user info
      }}
    >
      {/* Logout Button */}
      <Button
        variant="contained"
        color="error"
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          borderRadius: '20px',
          textTransform: 'none',
        }}
        onClick={() => navigate('/')} // Redirect to the landing page
      >
        Logout
      </Button>

      {/* Current User Section */}
      {userData && (
        <Box
          sx={{
            position: 'absolute',
            top: 16,
            left: 16,
            backgroundColor: '#fff',
            borderRadius: '15px',
            boxShadow: '0px 2px 5px rgba(0, 0, 0, 0.1)',
            padding: '8px 16px',
          }}
        >
          <Typography
            variant="body1"
            sx={{
              fontWeight: 'bold',
              color: '#333',
              cursor: 'pointer',
            }}
            onClick={handleMenuOpen} // Open dropdown menu on click
          >
            Welcome {userData.full_name}
          </Typography>
        </Box>
      )}

      {/* User Details Dropdown Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
      >
        <MenuItem>
          <Typography variant="body1">
            <strong>Full Name:</strong> {userData.full_name}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Age:</strong> {userData.age}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Gender:</strong> {userData.gender}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Height:</strong> {userData.height} cm
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Weight:</strong> {userData.weight} kg
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Daily Calories Intake:</strong> {userData.daily_calories_intake}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Resting Heart Rate:</strong> {userData.resting_heart_rate}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>VO2 Max:</strong> {userData.VO2_max}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Body Fat:</strong> {userData.body_fat}%
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Preferred Workout Type:</strong> {userData.workout_type}
          </Typography>
        </MenuItem>
      </Menu>

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

      {/* Recommended Buddies Section - Only show if there are recommendations */}
      {currentRecommendedBuddies.length > 0 && (
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
            Recommended Buddies
          </Typography>
          <Grid container spacing={3}>
            {currentRecommendedBuddies.map((buddy, index) => (
              <Grid item xs={12} sm={6} md={4} key={buddy.id_number}>
                <Fade
                  in={true} // Always true to enable fading
                  timeout={300} // Match the timeout with the setTimeout in replaceBuddy
                >
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
                      image={getRandomImageByGender(buddy.gender)} // Assign a random image based on gender
                      alt={buddy.full_name}
                    />
                    <CardContent>
                      <Stack direction="row" alignItems="center" justifyContent="center" spacing={1}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#333', textAlign: 'center' }}>
                          {buddy.full_name}, {buddy.age}
                        </Typography>
                        {buddy.gender.toLowerCase() === 'female' ? (
                          <FemaleIcon sx={{ color: '#e91e63' }} />
                        ) : (
                          <MaleIcon sx={{ color: '#2196f3' }} />
                        )}
                      </Stack>
                      <Stack direction="row" justifyContent="center" spacing={2} sx={{ mt: 1 }}>
                        <Typography variant="body2" sx={{ color: '#666' }}>
                          <strong>Height:</strong> {buddy.height} cm
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#666' }}>
                          <strong>Weight:</strong> {buddy.weight} kg
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#666' }}>
                          <strong>Preferred Workout Type:</strong> {buddy.workout_type}
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
                          onClick={() => handleDislikeRecommended(index)}
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
                          onClick={() => handleLikeRecommended(index)}
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
                </Fade>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

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
          Similar To You
        </Typography>
        {currentBuddies.length > 0 ? (
          <Grid container spacing={3}>
            {currentBuddies.map((buddy, index) => (
              <Grid item xs={12} sm={6} md={4} key={buddy.id_number}>
                <Fade
                  in={true} // Always true to enable fading
                  timeout={300} // Match the timeout with the setTimeout in replaceBuddy
                >
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
                      image={getRandomImageByGender(buddy.gender)} // Assign a random image based on gender
                      alt={buddy.full_name}
                    />
                    <CardContent>
                      <Stack direction="row" alignItems="center" justifyContent="center" spacing={1}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#333', textAlign: 'center' }}>
                          {buddy.full_name}, {buddy.age}
                        </Typography>
                        {buddy.gender.toLowerCase() === 'female' ? (
                          <FemaleIcon sx={{ color: '#e91e63' }} />
                        ) : (
                          <MaleIcon sx={{ color: '#2196f3' }} />
                        )}
                      </Stack>
                      <Stack direction="row" justifyContent="center" spacing={2} sx={{ mt: 1 }}>
                        <Typography variant="body2" sx={{ color: '#666' }}>
                          <strong>Height:</strong> {buddy.height} cm
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#666' }}>
                          <strong>Weight:</strong> {buddy.weight} kg
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#666' }}>
                          <strong>Preferred Workout Type:</strong> {buddy.workout_type}
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
                </Fade>
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
