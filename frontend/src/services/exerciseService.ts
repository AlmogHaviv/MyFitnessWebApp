export interface Exercise {
  id: number;
  name: string;
  description: string;
  category: string;
  targetMuscle: string;
  equipment: string;
  difficulty: string;
  videoUrl: string; // New property for YouTube video links
}

const exercises: Exercise[] = [
  {
    id: 0,
    name: 'Partner plank band row',
    description:
      'The partner plank band row is an abdominal exercise where two partners perform single-arm planks while rowing with a resistance band.',
    category: 'Strength',
    targetMuscle: 'Abdominals',
    equipment: 'Bands',
    difficulty: 'Intermediate',
    videoUrl: 'https://www.youtube.com/embed/Tili1UX_mJk', // Replace with actual video ID
  },
  {
    id: 1,
    name: 'Banded crunch isometric hold',
    description:
      'The banded crunch isometric hold is an exercise targeting the abdominal muscles, particularly the rectus abdominis.',
    category: 'Strength',
    targetMuscle: 'Abdominals',
    equipment: 'Bands',
    difficulty: 'Intermediate',
    videoUrl: 'https://www.youtube.com/embed/tXXsy0NphlI', // Replace with actual video ID
  },
  {
    id: 2,
    name: 'FYR Banded Plank Jack',
    description:
      'The banded plank jack is a variation on the plank that involves moving the legs in and out for repetitive motion.',
    category: 'Strength',
    targetMuscle: 'Abdominals',
    equipment: 'Bands',
    difficulty: 'Intermediate',
    videoUrl: 'https://www.youtube.com/embed/bqB0QZgur_w', // Replace with actual video ID
  },
  {
    id: 3,
    name: 'Banded crunch',
    description:
      'The banded crunch is an exercise targeting the abdominal muscles, particularly the rectus abdominis.',
    category: 'Strength',
    targetMuscle: 'Abdominals',
    equipment: 'Bands',
    difficulty: 'Intermediate',
    videoUrl: 'https://www.youtube.com/embed/dummy-video-3', // Replace with actual video ID
  },
  {
    id: 4,
    name: 'Crunch',
    description:
      'The crunch is a popular core exercise targeting the rectus abdominis, or "six-pack" muscles, as well as the obliques.',
    category: 'Strength',
    targetMuscle: 'Abdominals',
    equipment: 'Bands',
    difficulty: 'Intermediate',
    videoUrl: 'https://www.youtube.com/embed/dummy-video-4', // Replace with actual video ID
  },
  {
    id: 5,
    name: 'Decline band press sit-up',
    description:
      'The decline band press sit-up is a weighted core exercise that works the rectus abdominis or "six-pack" muscles.',
    category: 'Strength',
    targetMuscle: 'Abdominals',
    equipment: 'Bands',
    difficulty: 'Intermediate',
    videoUrl: 'https://www.youtube.com/embed/dummy-video-5', // Replace with actual video ID
  },
];

export const getSuggestedExercises = (): Exercise[] => {
  return exercises;
};

export interface Equipment {
  id: number;
  name: string;
  description: string;
  image: string;
  link: string;
}

const equipmentList: Equipment[] = [
  {
    id: 1,
    name: 'Resistance Bands',
    description: 'High-quality resistance bands for strength training and stretching.',
    image: 'https://m.media-amazon.com/images/I/71S4-NjoTDL._AC_UF1000,1000_QL80_.jpg',
    link: 'https://www.amazon.com',
  },
  {
    id: 2,
    name: 'Dumbbells',
    description: 'Adjustable dumbbells for versatile strength training.',
    image: 'https://m.media-amazon.com/images/I/91QxtmB7tEL.jpg',
    link: 'https://www.amazon.com',
  },
  {
    id: 3,
    name: 'Yoga Mat',
    description: 'Non-slip yoga mat for yoga, pilates, and floor exercises.',
    image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQm_MtpPJNhDzqbe674cHU_A-ZTPYxquR1cnA&s',
    link: 'https://www.amazon.com',
  },
  {
    id: 4,
    name: 'Kettlebell',
    description: 'Durable kettlebell for functional strength training.',
    image: 'https://via.placeholder.com/300x150',
    link: 'https://www.amazon.com',
  },
  {
    id: 5,
    name: 'Foam Roller',
    description: 'Foam roller for muscle recovery and deep tissue massage.',
    image: 'https://via.placeholder.com/300x150',
    link: 'https://www.amazon.com',
  },
];

export const getSuggestedEquipment = (): Equipment[] => {
  return equipmentList;
};