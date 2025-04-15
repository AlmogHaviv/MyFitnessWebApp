import React, { useState, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';

const LoginPage: React.FC = () => {
  const [ssn, setSsn] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleNext = () => {
    setError(null);
    setLoading(true);

    // Basic SSN validation (can be expanded)
    const isValid = /^\d{9}$/.test(ssn);
    if (!isValid) {
      setError('Please enter a valid 9-digit SSN.');
      setLoading(false);
      return;
    }

    // Simulate delay, then navigate
    setTimeout(() => {
      navigate('/land');
    }, 500);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSsn(e.target.value);
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          textAlign: 'center',
          mt: 8,
          mb: 4,
        }}
      >
        <LockIcon color="primary" sx={{ fontSize: 60 }} />
        <Typography variant="h4" gutterBottom>
          Secure Login
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Enter your SSN to continue
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper
        elevation={3}
        sx={{
          padding: 4,
          borderRadius: 3,
          backgroundColor: '#fff',
        }}
      >
        <TextField
          label="Social Security Number"
          placeholder="Enter 9-digit SSN"
          fullWidth
          variant="outlined"
          value={ssn}
          onChange={handleChange}
          inputProps={{ maxLength: 9 }}
          sx={{ mb: 3 }}
        />

        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={handleNext}
          disabled={loading}
          sx={{ borderRadius: '15px' }}
        >
          {loading ? <CircularProgress size={24} /> : 'Next'}
        </Button>
      </Paper>
    </Container>
  );
};

export default LoginPage;
