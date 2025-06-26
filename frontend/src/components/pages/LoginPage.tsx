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
import { getUserById } from '../../services/api';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [ssn, setSsn] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleNext = async () => {
    setError(null);
    setLoading(true);

    const isValid = /^\d{9}$/.test(ssn);
    if (!isValid) {
      setError('Please enter a valid 9-digit ID number.');
      setLoading(false);
      return;
    }

    try {
      const user = await getUserById(parseInt(ssn));
      console.log('User found:', user);
      localStorage.setItem('userData', JSON.stringify(user));
      navigate('/main');
    } catch (err: any) {
      setError('User not found or invalid ID.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSsn(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleNext();
    }
  };

  const handleSignup = () => {
    navigate('/land');
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
          Enter your ID number to continue
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
          label="ID Number"
          placeholder="Enter 9-digit IDs"
          fullWidth
          variant="outlined"
          value={ssn}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          inputProps={{ maxLength: 9 }}
          sx={{ mb: 3 }}
        />

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleNext}
          disabled={loading}
          sx={{ flex: 1, borderRadius: '15px' }}
        >
          {loading ? <CircularProgress size={24} /> : 'Login'}
        </Button>

        <Button
          variant="outlined"
          color="secondary"
          onClick={handleSignup}
          sx={{ flex: 1, borderRadius: '15px' }}
        >
          Signup
        </Button>
      </Box>

      </Paper>
    </Container>
  );
};

export default LoginPage;
