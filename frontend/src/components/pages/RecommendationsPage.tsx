import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, CircularProgress, Typography, Card, CardContent, Button, Grid, Box, CardMedia, Tooltip } from '@mui/material';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import { getWorkoutRecommendations } from '../../services/api';

const mockVideos = [
  {
    title: "Perfect Pushup Form Tutorial",
    url: "https://www.youtube.com/watch?v=_l3ySVKYVJ8",
    explanation: "Learn the fundamentals of pushup form and avoid common mistakes. This video covers hand placement, body alignment, and breathing techniques to maximize your pushup performance and prevent injuries. Whether you're a beginner or looking to refine your form, these tips will help you get the most out of your pushup workouts.",
  },
  {
    title: "Pushup Variations for Beginners",
    url: "https://www.youtube.com/watch?v=IODxDxX7oi4",
    explanation: "Try these beginner-friendly pushup variations to build strength and confidence. From knee pushups to incline pushups, this guide introduces modifications that make pushups accessible for everyone. Progress at your own pace and watch your upper body strength improve week by week.",
  },
  {
    title: "How to Increase Pushup Reps Fast",
    url: "https://www.youtube.com/watch?v=Eh00_rniF8E",
    explanation: "Tips and routines to quickly improve your pushup numbers. Discover effective training strategies, rest intervals, and supplemental exercises that target the muscles used in pushups. Stay consistent and track your progress to see rapid gains in endurance and strength.",
  },
];

const MAX_DESC_LENGTH = 220; 

const RecommendationsPage: React.FC = () => {
  const [videos, setVideos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [useMockVideos] = useState(false); // Set to true to use hardcoded videos
  const navigate = useNavigate();
  const hasFetched = useRef(false);

  useEffect(() => {
    if (useMockVideos) {
      setVideos(mockVideos);
      setLoading(false);
      return;
    }

    if (hasFetched.current) {
      return;
    }
    hasFetched.current = true;

    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    const query = localStorage.getItem('fitnessQuery') || '';

    if (!userData || !query) {
      navigate('/');
      return;
    }

    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const data = await getWorkoutRecommendations(userData, query);
        setVideos(data.workout_recommendations || []);
      } catch (err) {
        setVideos([]);
      }
      setLoading(false);
    };

    fetchRecommendations();
  }, [navigate, useMockVideos]);

  if (loading) {
    return (
      <Container sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 8 }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>Loading your personalized workout videos...</Typography>
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
      <Box sx={{ position: 'absolute', top: 24, left: 24, zIndex: 2 }}>
        <Button
          variant="contained"
          onClick={() => navigate('/main')}
          sx={{ borderRadius: '20px', textTransform: 'none' }}
        >
          Back to Main
        </Button>
      </Box>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <FitnessCenterIcon
          sx={{
            fontSize: '50px',
            color: '#007bff',
            mb: 1,
          }}
        />
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#333', mb: 1 }}>
          Personalized Workout Videos
        </Typography>
        <Typography variant="h5" sx={{ color: '#666' }}>
          Tailored just for you!
        </Typography>
      </Box>
      <Grid container spacing={3}>
        {videos.length === 0 && <Typography>No recommendations found.</Typography>}
        {videos.slice(0, 4).map((vid, idx) => {
          const isLong = vid.explanation.length > MAX_DESC_LENGTH;
          // Shorten at last space before limit for cleaner cut
          let displayText = vid.explanation;
          if (isLong) {
            const cutIdx = vid.explanation.lastIndexOf(' ', MAX_DESC_LENGTH);
            displayText = vid.explanation.slice(0, cutIdx > 0 ? cutIdx : MAX_DESC_LENGTH) + '...';
          }

          return (
            <Grid item xs={12} key={idx}>
              <Card
                sx={{
                  borderRadius: '20px',
                  boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
                  display: 'flex',
                  flexDirection: 'row',
                  alignItems: 'stretch',
                  minHeight: 220,
                }}
              >
                <CardMedia
                  component="iframe"
                  sx={{
                    width: 530,
                    minWidth: 320,
                    height: 300,
                    borderRadius: '20px 0 0 20px',
                    flexShrink: 0,
                  }}
                  src={vid.url.replace('watch?v=', 'embed/')}
                  title={vid.title}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
                <CardContent
                  sx={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'flex-start', 
                    p: 3,
                  }}
                >
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 'bold',
                      color: '#333',
                      mb: 2,
                      textAlign: 'left',
                    }}
                  >
                    Video Description:
                  </Typography>
                  <Box
                    sx={{
                      background: 'rgba(245,247,255,0.85)',
                      borderRadius: 2,
                      p: 2,
                      mb: 2.5,
                      minHeight: 60,
                      display: 'flex',
                      alignItems: 'center',
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#444',
                        textAlign: 'left',
                        fontSize: '1rem',
                        lineHeight: 1.6,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 4,
                        WebkitBoxOrient: 'vertical',
                        width: '100%',
                      }}
                    >
                      {displayText}
                    </Typography>
                  </Box>
                  {isLong && (
                    <Tooltip
                      title={
                        <Typography sx={{ p: 1, maxWidth: 350, whiteSpace: 'pre-line' }}>
                          {vid.explanation}
                        </Typography>
                      }
                      arrow
                      placement="top"
                    >
                      <Button
                        size="small"
                        sx={{
                          textTransform: 'none',
                          fontSize: '0.97rem',
                          alignSelf: 'flex-start',
                          mb: 1.5,
                          color: '#1976d2',
                          fontWeight: 600,
                          background: 'rgba(25, 118, 210, 0.07)',
                          borderRadius: 2,
                          px: 1.5,
                          py: 0.5,
                          '&:hover': {
                            background: 'rgba(25, 118, 210, 0.15)',
                          },
                        }}
                      >
                        Read more
                      </Button>
                    </Tooltip>
                  )}
                  <Button
                    variant="contained"
                    color="primary"
                    href={vid.url}
                    target="_blank"
                    sx={{
                      borderRadius: '20px',
                      textTransform: 'none',
                      alignSelf: 'flex-start',
                      mt: 1.5,
                    }}
                  >
                    Watch on YouTube
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Container>
  );
};

export default RecommendationsPage;