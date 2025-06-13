import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, CircularProgress, Typography, Card, CardContent, Button, Grid, Box, CardMedia } from '@mui/material';
import { getWorkoutRecommendations } from '../../services/api'; // adjust path as needed

const mockVideos = [
  {
    title: "Perfect Pushup Form Tutorial",
    url: "https://www.youtube.com/watch?v=_l3ySVKYVJ8",
    explanation: "Learn the fundamentals of pushup form and avoid common mistakes.",
    equipment: ["None"],
  },
  {
    title: "Pushup Variations for Beginners",
    url: "https://www.youtube.com/watch?v=IODxDxX7oi4",
    explanation: "Try these beginner-friendly pushup variations to build strength.",
    equipment: ["None"],
  },
  {
    title: "How to Increase Pushup Reps Fast",
    url: "https://www.youtube.com/watch?v=Eh00_rniF8E",
    explanation: "Tips and routines to quickly improve your pushup numbers.",
    equipment: ["None"],
  },
];

const RecommendationsPage: React.FC = () => {
  const [videos, setVideos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [useMockVideos] = useState(true); // Set to true to use hardcoded videos
  const navigate = useNavigate();

  useEffect(() => {
    if (useMockVideos) {
      setVideos(mockVideos);
      setLoading(false);
      return;
    }

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
        <Typography variant="h6" sx={{ mt: 2 }}>Loading recommendations...</Typography>
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
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#333', mb: 1 }}>
          Personalized Workout Videos
        </Typography>
        <Typography variant="subtitle1" sx={{ color: '#666' }}>
          Tailored just for you!
        </Typography>
      </Box>
      <Grid container spacing={3}>
        {videos.length === 0 && <Typography>No recommendations found.</Typography>}
        {videos.map((vid, idx) => (
          <Grid item xs={12} sm={6} md={4} key={idx}>
            <Card
              sx={{
                borderRadius: '20px',
                boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.1)',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <CardMedia
                component="iframe"
                height="200"
                src={vid.url.replace('watch?v=', 'embed/')}
                title={vid.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#333' }}>
                  {vid.title}
                </Typography>
                <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>
                  {vid.explanation}
                </Typography>
                <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>
                  <strong>Equipment:</strong> {Array.isArray(vid.equipment) ? vid.equipment.join(', ') : vid.equipment}
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  href={vid.url}
                  target="_blank"
                  sx={{
                    borderRadius: '20px',
                    textTransform: 'none',
                  }}
                >
                  Watch on YouTube
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Button
        variant="contained"
        onClick={() => window.history.back()}
        sx={{ mt: 4, borderRadius: '20px', textTransform: 'none' }}
      >
        Back to Main
      </Button>
    </Container>
  );
};

export default RecommendationsPage;