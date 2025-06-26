import React, { useState, useEffect, useRef } from 'react';
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
  Stack,
  Grid,
  Paper,
  TextField,
  IconButton,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CloseIcon from '@mui/icons-material/Close';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import Fade from '@mui/material/Fade';
import MaleIcon from '@mui/icons-material/Male';
import FemaleIcon from '@mui/icons-material/Female';
import SendIcon from '@mui/icons-material/Send';
import PhoneIphoneIcon from '@mui/icons-material/PhoneIphone';
import { getSimilarUsers, recommendBuddies, logEvent } from '../../services/api';
import { getRandomImageByGender } from '../../services/imageStock';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Grow from '@mui/material/Grow';
import Avatar from '@mui/material/Avatar';

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
  imageUrl?: string;
}

const MainPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fitnessQuery, setFitnessQuery] = useState(''); // State for fitness query

  // States for "Similar Buddies" - always show 3
  const [buddies, setBuddies] = useState<Buddy[]>([]);
  const [displayedSimilarBuddies, setDisplayedSimilarBuddies] = useState<Buddy[]>([]);
  const [likedSimilarBuddies, setLikedSimilarBuddies] = useState<Set<number>>(new Set());
  const [similarBuddyIndex, setSimilarBuddyIndex] = useState(0);

  // States for "Recommended Buddies" - always show 6
  const [recommendedBuddies, setRecommendedBuddies] = useState<Buddy[]>([]);
  const [displayedRecommendedBuddies, setDisplayedRecommendedBuddies] = useState<Buddy[]>([]);
  const [likedRecommendedBuddies, setLikedRecommendedBuddies] = useState<Set<number>>(new Set());
  const [recommendedBuddyIndex, setRecommendedBuddyIndex] = useState(0);

  const [userAvatar, setUserAvatar] = useState<string>('');
  const [userData, setUserData] = useState<any>(null);
  const [animationDirection, setAnimationDirection] = useState<'left' | 'right' | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Add refs to track like timeouts
  const likeTimeoutsSimilar = useRef<{ [key: number]: NodeJS.Timeout }>({});
  const likeTimeoutsRecommended = useRef<{ [key: number]: NodeJS.Timeout }>({});

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
        setUserAvatar(getRandomImageByGender(parsedUserData.gender));

        // Fetch similar buddies
        const similarUsersResponse = await getSimilarUsers(parsedUserData);
        const similarUsersArray = (
          Array.isArray(similarUsersResponse)
            ? similarUsersResponse
            : similarUsersResponse.similar_users || []
        ).map((buddy: Buddy) => ({
          ...buddy,
          imageUrl: getRandomImageByGender(buddy.gender),
        }));
        setBuddies(similarUsersArray);
        setDisplayedSimilarBuddies(similarUsersArray.slice(0, 3)); // Show first 3
        setSimilarBuddyIndex(3); // Next index to show

        // Fetch recommended buddies
        const recommendations = await recommendBuddies(String(parsedUserData.id_number));
        const recommendedBuddiesWithImages = recommendations.recommended_buddies.map((buddy: Buddy) => ({
          ...buddy,
          imageUrl: getRandomImageByGender(buddy.gender),
        }));
        setRecommendedBuddies(recommendedBuddiesWithImages);
        setDisplayedRecommendedBuddies(recommendedBuddiesWithImages.slice(0, 6)); // Show first 6
        setRecommendedBuddyIndex(6); // Next index to show
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred while fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  // Handle like for similar buddies
  const handleLikeSimilar = async (buddyIndex: number) => {
    const buddy = displayedSimilarBuddies[buddyIndex];
    setLikedSimilarBuddies(prev => new Set(prev).add(buddy.id_number));
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'like');
      console.log('Logged event: ', userData.full_name, 'Liked', buddy.full_name);
    } catch (error) {
      console.error('Error logging like event:', error);
    }
    if (likeTimeoutsSimilar.current[buddyIndex]) {
      clearTimeout(likeTimeoutsSimilar.current[buddyIndex]);
    }
    likeTimeoutsSimilar.current[buddyIndex] = setTimeout(() => {
      replaceWithNextSimilarBuddy(buddyIndex);
      delete likeTimeoutsSimilar.current[buddyIndex];
    }, 3000);
  };

  // Handle dislike for similar buddies
  const handleDislikeSimilar = async (buddyIndex: number) => {
    if (likeTimeoutsSimilar.current[buddyIndex]) {
      clearTimeout(likeTimeoutsSimilar.current[buddyIndex]);
      delete likeTimeoutsSimilar.current[buddyIndex];
    }
    const buddy = displayedSimilarBuddies[buddyIndex];
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'dislike');
      console.log('Logged event: ', userData.full_name, 'Disliked', buddy.full_name);
    } catch (error) {
      console.error('Error logging dislike event:', error);
    }
    replaceWithNextSimilarBuddy(buddyIndex);
  };

  // Replace similar buddy with next available one
  const replaceWithNextSimilarBuddy = (buddyIndex: number) => {
    setDisplayedSimilarBuddies(prev => {
      if (similarBuddyIndex < buddies.length) {
        const newDisplayed = [...prev];
        newDisplayed[buddyIndex] = buddies[similarBuddyIndex];
        setSimilarBuddyIndex(prevIdx => prevIdx + 1);
        return newDisplayed;
      } else {
        // No more buddies, remove this slot
        return prev.filter((_, index) => index !== buddyIndex);
      }
    });
  };

  // Handle like for recommended buddies
  const handleLikeRecommended = async (buddyIndex: number) => {
    const buddy = displayedRecommendedBuddies[buddyIndex];
    setLikedRecommendedBuddies(prev => new Set(prev).add(buddy.id_number));
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'like');
      console.log('Logged event: ', userData.full_name, 'Liked Recommended', buddy.full_name);
    } catch (error) {
      console.error('Error logging like event for recommended buddy:', error);
    }
    if (likeTimeoutsRecommended.current[buddyIndex]) {
      clearTimeout(likeTimeoutsRecommended.current[buddyIndex]);
    }
    likeTimeoutsRecommended.current[buddyIndex] = setTimeout(() => {
      replaceWithNextRecommendedBuddy(buddyIndex);
      delete likeTimeoutsRecommended.current[buddyIndex];
    }, 3000);
  };

  // Handle dislike for recommended buddies
  const handleDislikeRecommended = async (buddyIndex: number) => {
    if (likeTimeoutsRecommended.current[buddyIndex]) {
      clearTimeout(likeTimeoutsRecommended.current[buddyIndex]);
      delete likeTimeoutsRecommended.current[buddyIndex];
    }
    const buddy = displayedRecommendedBuddies[buddyIndex];
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'dislike');
      console.log('Logged event: ', userData.full_name, 'Disliked Recommended', buddy.full_name);
    } catch (error) {
      console.error('Error logging dislike event for recommended buddy:', error);
    }
    replaceWithNextRecommendedBuddy(buddyIndex);
  };

  // Replace recommended buddy with next available one
  const replaceWithNextRecommendedBuddy = (buddyIndex: number) => {
    setDisplayedRecommendedBuddies(prev => {
      if (recommendedBuddyIndex < recommendedBuddies.length) {
        const newDisplayed = [...prev];
        newDisplayed[buddyIndex] = recommendedBuddies[recommendedBuddyIndex];
        setRecommendedBuddyIndex(prevIdx => prevIdx + 1);
        return newDisplayed;
      } else {
        // No more buddies, remove this slot
        return prev.filter((_, index) => index !== buddyIndex);
      }
    });
  };

  // Handle hide phone number for similar buddies
  const handleHideSimilarBuddy = (buddyIndex: number) => {
    setLikedSimilarBuddies(prev => {
      const newSet = new Set(prev);
      newSet.delete(displayedSimilarBuddies[buddyIndex].id_number);
      return newSet;
    });
    replaceWithNextSimilarBuddy(buddyIndex);
  };

  // Handle hide phone number for recommended buddies
  const handleHideRecommendedBuddy = (buddyIndex: number) => {
    setLikedRecommendedBuddies(prev => {
      const newSet = new Set(prev);
      newSet.delete(displayedRecommendedBuddies[buddyIndex].id_number);
      return newSet;
    });
    replaceWithNextRecommendedBuddy(buddyIndex);
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
        position: 'relative',
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
        onClick={() => navigate('/')}
      >
        Logout
      </Button>

      {/* Current User Section */}
      {userData && (
        <Box
          sx={{
            position: 'absolute',
            top: 24,
            left: 24,
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'transparent',
            boxShadow: 'none',
            padding: 0,
            zIndex: 2,
          }}
        >
          <Avatar
            src={userAvatar}
            alt={userData.full_name}
            sx={{
              width: 56,
              height: 56,
              mr: 1.5,
              border: '2.5px solid #fff',
              boxShadow: '0 2px 8px rgba(0,0,0,0.10)',
              background: '#f5f5f5',
              cursor: 'pointer',
            }}
            onClick={handleMenuOpen}
          />
          <Typography
            variant="body1"
            sx={{
              fontWeight: 600,
              color: '#222',
              cursor: 'pointer',
              background: 'rgba(255,255,255,0.85)',
              borderRadius: '20px',
              px: 2,
              py: 1,
              boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
              fontSize: 18,
              transition: 'background 0.2s',
              '&:hover': {
                background: 'rgba(245,245,245,0.95)',
              },
            }}
            onClick={handleMenuOpen}
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
            <strong>Full Name:</strong> {userData?.full_name}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Age:</strong> {userData?.age}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Gender:</strong> {userData?.gender}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Height:</strong> {userData?.height} cm
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Weight:</strong> {userData?.weight} kg
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Daily Calories Intake:</strong> {userData?.daily_calories_intake}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Resting Heart Rate:</strong> {userData?.resting_heart_rate}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>VO2 Max:</strong> {userData?.VO2_max}
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Body Fat:</strong> {userData?.body_fat}%
          </Typography>
        </MenuItem>
        <MenuItem>
          <Typography variant="body1">
            <strong>Preferred Workout Type:</strong> {userData?.workout_type}
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
          Find your perfect personalized fitness experience
        </Typography>
      </Box>

      {/* Fitness Goal - Query Input Section */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          mb: 3,
          mt: 2,
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 3,
            borderRadius: '16px',
            backgroundColor: '#ffff',
            boxShadow: '0px 4px 10px rgba(0,0,0,0.08)',
            width: { xs: 800, sm: 1500, md: 1500 },
          }}
        >
          <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                color: '#333',
                textAlign: 'center',
              }}
            >
              What is your fitness goal?
            </Typography>
          </Box>
          <Box
            sx={{
              width: '100%',
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <TextField
              fullWidth
              placeholder="e.g. I want to get better at pushups"
              value={fitnessQuery}
              onChange={e => setFitnessQuery(e.target.value)}
              variant="outlined"
              size="small"
              sx={{
                backgroundColor: '#fff',
                borderRadius: '8px',
              }}
              InputProps={{
                style: { fontSize: '0.95rem', padding: '6px 10px', height: 36 },
                endAdornment: (
                  <IconButton
                    color="primary"
                    disabled={!fitnessQuery.trim()}
                    onClick={() => {
                      localStorage.setItem('fitnessQuery', fitnessQuery);
                      navigate('/recommendations');
                    }}
                    sx={{
                      borderRadius: '50%',
                      ml: 1,
                    }}
                  >
                    <SendIcon />
                  </IconButton>
                ),
              }}
            />
          </Box>
        </Paper>
      </Box>

      {/* Similar Buddies Section - Always show 3 */}
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
          variant="h5"
          sx={{
            fontWeight: 'bold',
            color: '#333',
            mb: 2,
          }}
        >
          Similar Fitness Buddies
        </Typography>
        {displayedSimilarBuddies.length > 0 ? (
          <Grid container spacing={3}>
            {displayedSimilarBuddies.map((buddy, index) => (
              <Grid item xs={12} sm={6} md={4} key={buddy.id_number}>
                <Grow in timeout={600}>
                  <Card
                    sx={{
                      borderRadius: '20px',
                      boxShadow: '0px 2px 12px rgba(0,0,0,0.10)',
                      transition: 'box-shadow 0.3s, transform 0.3s, background 0.3s',
                      '&:hover': {
                        boxShadow: '0px 6px 24px rgba(0,0,0,0.16)',
                        transform: 'scale(1.02)',
                      },
                      background: likedSimilarBuddies.has(buddy.id_number) ? '#f6f7fa' : '#fff',
                    }}
                  >
                    {likedSimilarBuddies.has(buddy.id_number) ? (
                      <Fade in timeout={1200}>
                        <CardContent>
                          <CardMedia
                            component="img"
                            height="300"
                            image={buddy.imageUrl}
                            alt={buddy.full_name}
                            sx={{
                              filter: 'grayscale(0.15) brightness(0.98)',
                              borderRadius: '20px 20px 0 0',
                              transition: 'filter 0.3s',
                              mb: 2,
                            }}
                          />
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              mt: 2,
                              mb: 2,
                              minHeight: 56,
                            }}
                          >
                            <PhoneIphoneIcon sx={{ fontSize: 32, color: '#555', mr: 1.5 }} />
                            <Typography
                              variant="h6"
                              sx={{
                                textAlign: 'center',
                                color: '#222',
                                fontWeight: 500,
                                fontSize: 22,
                              }}
                            >
                              052-5381648
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                            <Button
                              variant="outlined"
                              color="error"
                              onClick={() => handleHideSimilarBuddy(index)}
                              sx={{
                                borderRadius: '50%',
                                minWidth: 40,
                                width: 40,
                                height: 40,
                                p: 0,
                                fontSize: 20,
                              }}
                            >
                              X
                            </Button>
                          </Box>
                        </CardContent>
                      </Fade>
                    ) : (
                      <>
                        <CardMedia
                          component="img"
                          height="300"
                          image={buddy.imageUrl}
                          alt={buddy.full_name}
                          sx={{
                            borderRadius: '20px 20px 0 0',
                          }}
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
                              onClick={() => handleDislikeSimilar(index)}
                              sx={{ borderRadius: '20px', textTransform: 'none' }}
                            >
                              Dislike
                            </Button>
                            <Button
                              variant="contained"
                              color="success"
                              startIcon={<FavoriteIcon />}
                              onClick={() => handleLikeSimilar(index)}
                              sx={{ borderRadius: '20px', textTransform: 'none' }}
                            >
                              Like
                            </Button>
                          </Stack>
                        </CardContent>
                      </>
                    )}
                  </Card>
                </Grow>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography variant="body1" sx={{ color: '#666', textAlign: 'center', mt: 2 }}>
            No more matches available. Check back later for new workout buddies!
          </Typography>
        )}
      </Box>

      {/* Recommended Buddies Section - Always show 6 */}
      {displayedRecommendedBuddies.length > 0 && (
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
            variant="h5"
            sx={{
              fontWeight: 'bold',
              color: '#333',
              mb: 2,
            }}
          >
            Recommended Fitness Buddies
          </Typography>
          <Grid container spacing={3}>
            {displayedRecommendedBuddies.map((buddy, index) => (
              <Grid item xs={12} sm={6} md={4} key={buddy.id_number}>
                <Grow in timeout={600}>
                  <Card
                    sx={{
                      borderRadius: '20px',
                      boxShadow: '0px 2px 12px rgba(0,0,0,0.10)',
                      transition: 'box-shadow 0.3s, transform 0.3s, background 0.3s',
                      '&:hover': {
                        boxShadow: '0px 6px 24px rgba(0,0,0,0.16)',
                        transform: 'scale(1.02)',
                      },
                      background: likedRecommendedBuddies.has(buddy.id_number) ? '#f6f7fa' : '#fff',
                    }}
                  >
                    {likedRecommendedBuddies.has(buddy.id_number) ? (
                      <Fade in timeout={1200}>
                        <CardContent>
                          <CardMedia
                            component="img"
                            height="300"
                            width="300"
                            image={buddy.imageUrl}
                            alt={buddy.full_name}
                            sx={{
                              filter: 'grayscale(0.15) brightness(0.98)',
                              borderRadius: '20px 20px 0 0',
                              transition: 'filter 0.3s',
                              mb: 2,
                            }}
                          />
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              mt: 2,
                              mb: 2,
                              minHeight: 56,
                            }}
                          >
                            <PhoneIphoneIcon sx={{ fontSize: 32, color: '#555', mr: 1.5 }} />
                            <Typography
                              variant="h6"
                              sx={{
                                textAlign: 'center',
                                color: '#222',
                                fontWeight: 500,
                                fontSize: 22,
                              }}
                            >
                              052-5381648
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                            <Button
                              variant="outlined"
                              color="error"
                              onClick={() => handleHideRecommendedBuddy(index)}
                              sx={{
                                borderRadius: '50%',
                                minWidth: 40,
                                width: 40,
                                height: 40,
                                p: 0,
                                fontSize: 20,
                              }}
                            >
                              X
                            </Button>
                          </Box>
                        </CardContent>
                      </Fade>
                    ) : (
                      <>
                        <CardMedia
                          component="img"
                          height="300"
                          width="300"
                          image={buddy.imageUrl}
                          alt={buddy.full_name}
                          sx={{
                            filter: 'grayscale(0.10) brightness(1)',
                            borderRadius: '20px 20px 0 0',
                            transition: 'filter 0.3s',
                          }}
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
                              sx={{ borderRadius: '20px', textTransform: 'none' }}
                            >
                              Dislike
                            </Button>
                            <Button
                              variant="contained"
                              color="success"
                              startIcon={<FavoriteIcon />}
                              onClick={() => handleLikeRecommended(index)}
                              sx={{ borderRadius: '20px', textTransform: 'none' }}
                            >
                              Like
                            </Button>
                          </Stack>
                        </CardContent>
                      </>
                    )}
                  </Card>
                </Grow>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
};

export default MainPage;
