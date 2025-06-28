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
  Stack,
  Grid,
  Paper,
  TextField,
  IconButton,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CloseIcon from '@mui/icons-material/Close';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import Fade from '@mui/material/Fade';
import MaleIcon from '@mui/icons-material/Male';
import FemaleIcon from '@mui/icons-material/Female';
import SendIcon from '@mui/icons-material/Send';
import PhoneIphoneIcon from '@mui/icons-material/PhoneIphone';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import PersonIcon from '@mui/icons-material/Person';
import Tooltip from '@mui/material/Tooltip';
import { getSimilarUsers, recommendBuddies, logEvent } from '../../services/api';
import { getRandomImageByGender } from '../../services/imageStock';
import Menu from '@mui/material/Menu';
import Avatar from '@mui/material/Avatar';
import Grow from '@mui/material/Grow';
import Slider from '@mui/material/Slider';

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

  // States for "Similar Buddies" - always show 6
  const [buddies, setBuddies] = useState<Buddy[]>([]);
  const [showPhoneNumberSimilar, setShowPhoneNumberSimilar] = useState<{ [id: number]: boolean }>({});
  const [removedSimilarIds, setRemovedSimilarIds] = useState<Set<number>>(new Set());

  // States for "Recommended Buddies" - always show 3
  const [recommendedBuddies, setRecommendedBuddies] = useState<Buddy[]>([]);
  const [showPhoneNumberRecommended, setShowPhoneNumberRecommended] = useState<{ [id: number]: boolean }>({});
  const [removedRecommendedIds, setRemovedRecommendedIds] = useState<Set<number>>(new Set());

  const [userAvatar, setUserAvatar] = useState<string>('');
  const [userData, setUserData] = useState<any>(null);
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

        // Fetch recommended buddies
        const recommendations = await recommendBuddies(String(parsedUserData.id_number));
        const recommendedBuddiesWithImages = recommendations.recommended_buddies.map((buddy: Buddy) => ({
          ...buddy,
          imageUrl: getRandomImageByGender(buddy.gender),
        }));
        setRecommendedBuddies(recommendedBuddiesWithImages);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred while fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  // Filter buddies based on selected filters
  const [genderFilter, setGenderFilter] = useState<string>('all');
  const [workoutTypeFilter, setWorkoutTypeFilter] = useState<string>('all');
  const [ageRange, setAgeRange] = useState<number[]>([18, 60]);

  // New pending states for filters
  const [pendingGenderFilter, setPendingGenderFilter] = useState(genderFilter);
  const [pendingWorkoutTypeFilter, setPendingWorkoutTypeFilter] = useState(workoutTypeFilter);
  const [pendingAgeRange, setPendingAgeRange] = useState(ageRange);

  // Filter both similar and recommended buddies
  const filteredSimilarBuddies = buddies.filter(buddy =>
    !removedSimilarIds.has(buddy.id_number) &&
    (genderFilter === 'all' || (buddy.gender?.toLowerCase().trim() === genderFilter)) &&
    (workoutTypeFilter === 'all' || buddy.workout_type === workoutTypeFilter) &&
    buddy.age >= ageRange[0] && buddy.age <= ageRange[1]
  );

  const filteredRecommendedBuddies = recommendedBuddies.filter(buddy =>
    !removedRecommendedIds.has(buddy.id_number) &&
    (genderFilter === 'all' || (buddy.gender?.toLowerCase().trim() === genderFilter)) &&
    (workoutTypeFilter === 'all' || buddy.workout_type === workoutTypeFilter) &&
    buddy.age >= ageRange[0] && buddy.age <= ageRange[1]
  );

  // Always show up to 3 recommended buddies
  const displayedRecommended = filteredRecommendedBuddies.slice(0, 3);

  // Always show up to 6 similar buddies
  const displayedSimilar = filteredSimilarBuddies.slice(0, 6);

  // Get unique workout types for dropdown
  const allWorkoutTypes = Array.from(new Set([
    ...buddies.map(b => b.workout_type),
    ...recommendedBuddies.map(b => b.workout_type),
  ])).filter(Boolean);

  const handleApplyFilters = () => {
    setGenderFilter(pendingGenderFilter);
    setWorkoutTypeFilter(pendingWorkoutTypeFilter);
    setAgeRange(pendingAgeRange);
  };

  // Handle like for recommended buddies
  const handleLikeRecommended = async (buddyIndex: number) => {
    const buddy = displayedRecommended[buddyIndex];
    setShowPhoneNumberRecommended(prev => ({ ...prev, [buddy.id_number]: true }));
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'like');
      console.log('Logged event: ', userData.full_name, 'Liked', buddy.full_name);
    } catch (error) {
      console.error('Error logging like event for recommended buddy:', error);
    }
  };

  // Handle dislike for recommended buddies
  const handleDislikeRecommended = async (buddyIndex: number) => {
    const buddy = displayedRecommended[buddyIndex];
    setRemovedRecommendedIds(prev => new Set(prev).add(buddy.id_number));
    setShowPhoneNumberRecommended(prev => {
      const newState = { ...prev };
      delete newState[buddy.id_number];
      return newState;
    });
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'dislike');
      console.log('Logged event: ', userData.full_name, 'Disliked', buddy.full_name);
    } catch (error) {
      console.error('Error logging dislike event for recommended buddy:', error);
    }
  };

  // Handle hide phone number for recommended buddies
  const handleHideRecommendedBuddy = (buddyIndex: number) => {
    const buddy = displayedRecommended[buddyIndex];
    setRemovedRecommendedIds(prev => new Set(prev).add(buddy.id_number));
    setShowPhoneNumberRecommended(prev => {
      const newState = { ...prev };
      delete newState[buddy.id_number];
      return newState;
    });
  };

  // Handle like for similar buddies
  const handleLikeSimilar = async (buddyIndex: number) => {
    const buddy = displayedSimilar[buddyIndex];
    setShowPhoneNumberSimilar(prev => ({ ...prev, [buddy.id_number]: true }));
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'like');
      console.log('Logged event: ', userData.full_name, 'Liked', buddy.full_name);
    } catch (error) {
      console.error('Error logging like event:', error);
    }
  };

  // Handle dislike for similar buddies
  const handleDislikeSimilar = async (buddyIndex: number) => {
    const buddy = displayedSimilar[buddyIndex];
    setRemovedSimilarIds(prev => new Set(prev).add(buddy.id_number));
    setShowPhoneNumberSimilar(prev => {
      const newState = { ...prev };
      delete newState[buddy.id_number];
      return newState;
    });
    try {
      await logEvent(String(userData.id_number), String(buddy.id_number), 'dislike');
      console.log('Logged event: ', userData.full_name, 'Disliked', buddy.full_name);
    } catch (error) {
      console.error('Error logging dislike event:', error);
    }
  };

  // Handle hide phone number for similar buddies
  const handleHideSimilarBuddy = (buddyIndex: number) => {
    const buddy = displayedSimilar[buddyIndex];
    setRemovedSimilarIds(prev => new Set(prev).add(buddy.id_number));
    setShowPhoneNumberSimilar(prev => {
      const newState = { ...prev };
      delete newState[buddy.id_number];
      return newState;
    });
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
          <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center', mb: 2, alignItems: 'center', gap: 1 }}>
            <AutoAwesomeIcon sx={{ fontSize: 32, color: '#FFD700', mr: 1 }} />
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                color: '#333',
                textAlign: 'center',
              }}
            >
              Tell us what is your fitness goal and we will find the best workouts videos for you
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

      {/* Filter Controls - Shared between both sections */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4, justifyContent: 'center', alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel id="gender-filter-label">Gender</InputLabel>
          <Select
            labelId="gender-filter-label"
            value={pendingGenderFilter}
            label="Gender"
            onChange={e => setPendingGenderFilter(e.target.value)}
            size="small"
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="male">Male</MenuItem>
            <MenuItem value="female">Female</MenuItem>
            <MenuItem value="other">Other</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 160 }}>
          <InputLabel id="workout-type-filter-label">Workout Type</InputLabel>
          <Select
            labelId="workout-type-filter-label"
            value={pendingWorkoutTypeFilter}
            label="Workout Type"
            onChange={e => setPendingWorkoutTypeFilter(e.target.value)}
            size="small"
          >
            <MenuItem value="all">All</MenuItem>
            {allWorkoutTypes.map(type => (
              <MenuItem key={type} value={type}>{type}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <Box sx={{ display: 'flex', alignItems: 'center', width: 320, px: 2 }}>
          <InputLabel id="age-range-label" sx={{ minWidth: 70, mr: 3, fontWeight: 500, color: 'text.primary' }}>
            Age Range:   
          </InputLabel>
          <Slider
            value={pendingAgeRange}
            onChange={(_, newValue) => setPendingAgeRange(newValue as number[])}
            valueLabelDisplay="on"
            min={16}
            max={80}
            step={1}
            sx={{
              flex: 1,
              '& .MuiSlider-valueLabel': {
                top: 48,
                background: 'transparent',
                color: '#1976d2',
                fontWeight: 700,
                fontSize: 16,
                borderRadius: 4,
                padding: '2px 10px',
                minWidth: 32,
              },
            }}
          />
        </Box>
        <Button
          variant="contained"
          color="primary"
          onClick={handleApplyFilters}
          sx={{ ml: 2, height: 40 }}
        >
          Apply Filters
        </Button>
      </Box>

      {/* Similar Buddies Section - Always show 6 */}
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
          People Similar to You Loved These Fitness Buddies
        </Typography>
        {displayedSimilar.length > 0 ? (
          <Grid container spacing={3}>
            {displayedSimilar.map((buddy, index) => (
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
                      background: showPhoneNumberSimilar[buddy.id_number] ? '#f6f7fa' : '#fff',
                    }}
                  >
                    {showPhoneNumberSimilar[buddy.id_number] ? (
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
                            {(() => {
                              const gender = buddy.gender?.toLowerCase();
                              let icon = null;
                              let label = '';
                              if (gender === 'female') {
                                icon = <FemaleIcon sx={{ color: '#e91e63' }} />;
                                label = 'Female';
                              } else if (gender === 'male') {
                                icon = <MaleIcon sx={{ color: '#2196f3' }} />;
                                label = 'Male';
                              } else {
                                icon = <PersonIcon sx={{ color: '#9e9e9e' }} />;
                                label = 'Other';
                              }
                              return <Tooltip title={label} slotProps={{ tooltip: { sx: { fontSize: '1.2rem', fontWeight: 600 } } }}>{icon}</Tooltip>;
                            })()}
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
            No matches found.
          </Typography>
        )}
      </Box>

      {/* Recommended Buddies Section - Only show if there are recommendations */}
      {recommendedBuddies.length > 0 && (
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
            Recommended Fitness Buddies Based on Your Activity
          </Typography>
          {displayedRecommended.length === 0 ? (
            <Typography variant="body1" sx={{ color: '#666', textAlign: 'center', mt: 2 }}>
              No matches found.
            </Typography>
          ) : (
            <Grid container spacing={3}>
              {displayedRecommended.map((buddy, index) => (
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
                        background: showPhoneNumberRecommended[buddy.id_number] ? '#f6f7fa' : '#fff',
                      }}
                    >
                      {showPhoneNumberRecommended[buddy.id_number] ? (
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
                              {(() => {
                                const gender = buddy.gender?.toLowerCase();
                                let icon = null;
                                let label = '';
                                if (gender === 'female') {
                                  icon = <FemaleIcon sx={{ color: '#e91e63' }} />;
                                  label = 'Female';
                                } else if (gender === 'male') {
                                  icon = <MaleIcon sx={{ color: '#2196f3' }} />;
                                  label = 'Male';
                                } else {
                                  icon = <PersonIcon sx={{ color: '#9e9e9e' }} />;
                                  label = 'Other';
                                }
                                return <Tooltip title={label} slotProps={{ tooltip: { sx: { fontSize: '1.2rem', fontWeight: 600 } } }}>{icon}</Tooltip>;
                              })()}
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
          )}
        </Box>
      )}
    </Container>
  );
};

export default MainPage;
