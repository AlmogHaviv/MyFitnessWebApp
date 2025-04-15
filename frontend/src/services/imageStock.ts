export const femaleImages = [
  'https://routines.club/wp-content/uploads/2024/11/Taylor-Swift-Training.jpg',
];

export const maleImages = [
  'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOpcqwKPSVagiOZL1Gz98sOgPlUY2vyUeJmQ&s',
];

/**
 * Randomly selects an image based on gender.
 * @param gender - The gender of the buddy ('male' or 'female').
 * @returns A random image URL.
 */
export const getRandomImageByGender = (gender: string): string => {
  if (gender.toLowerCase() === 'female') {
    return femaleImages[Math.floor(Math.random() * femaleImages.length)];
  } else {
    return maleImages[Math.floor(Math.random() * maleImages.length)];
  }
};