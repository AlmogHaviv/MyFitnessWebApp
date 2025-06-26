export const femaleImages = [
  'https://routines.club/wp-content/uploads/2024/11/Taylor-Swift-Training.jpg',
  'https://media.self.com/photos/5b52046f18a2407a16eba501/4:3/w_2560%2Cc_limit/woman-lifting-dumbbells.jpg',
  'https://media.istockphoto.com/id/1470234996/photo/woman-sitting-in-a-fitness-studio-with-her-yoga-class.jpg?s=612x612&w=0&k=20&c=PW0frpWedwpoux9hNCuVuzYYLsRSQxo0FtLtPYOk14c=',
  'https://hips.hearstapps.com/hmg-prod/images/gym-workout-66d087d56ef90.jpg?fill=4:3&resize=1200:*',
  'https://media.istockphoto.com/id/1265038811/photo/beautiful-young-woman-training-with-kettlebell-in-gym.jpg?s=612x612&w=0&k=20&c=MfMSFaBSk8JYPj64aqtFfo1HVdY5RIKoh5l2UCdEvls=',
  'https://www.shape.com/thmb/C8ClEyptJt8-D_KQ_8K_GxNv20Y=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Muscle-Building-Workout-Plan-GettyImages-1339018482-2000-8db6490ebaee4270898e0f6590b910fa.jpg',
  'https://www.uhhospitals.org/-/media/images/social/woman-planks-gym-1478822293-blog-opengraph.jpg',
  'https://www.usnews.com/object/image/00000183-8f4a-dfce-a3eb-ef7a1c7d0000/gettyimages-1288737452.jpg?update-time=1664556556781&size=responsive640',
  'https://cdn.shopify.com/s/files/1/0243/9315/4623/files/30-minute-dumbbell-workout-plan.jpg?v=1620800289',
  'https://cdn.shopify.com/s/files/1/0618/9462/3460/files/healthy-asian-athlete-woman-sportswear-600nw-2131540853.jpg',
  'https://cbx-prod.b-cdn.net/COLOURBOX63719963.jpg?width=800&height=800&quality=70',
  'https://www.gymshark.com/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fwl6q2in9o7k3%2F4OZlDbR08bgoQ5DeR8rSPe%2F287d4e5702f7d22b700548ef8ff64ff7%2FHeadless_Cards_-_23024609.png&w=1664&q=85',
];

export const maleImages = [
  'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOpcqwKPSVagiOZL1Gz98sOgPlUY2vyUeJmQ&s',
  'https://media.istockphoto.com/id/1449353914/photo/fitness-gym-and-black-man-doing-a-workout-with-weights-for-strength-wellness-and-training.jpg?s=612x612&w=0&k=20&c=ozKkP-4W7Fg7c77s3-gE7QsxX51BJVEKi6LOxIMk8M0=',
  'https://images.stockcake.com/public/c/5/b/c5bf2df4-8459-44d0-b644-6f8b93943aa5_large/gymnast-training-hard-stockcake.jpg',
  'https://www.mensjournal.com/.image/t_share/MTk2MTM1OTA0MTc5NDYzMzEz/2-the-zac-efron-workout-to-get-a-beach-ready-baywatch-body.jpg',
  'https://hips.hearstapps.com/hmg-prod/images/dwayne-johnson-aka-the-rock-is-seen-after-a-work-out-at-news-photo-1598469836.jpg?crop=1.00xw:0.668xh;0,0.0890xh&resize=980:*',
  'https://hips.hearstapps.com/hmg-prod/images/701/articles/2017/05/zac-efron-got-ripped-for-baywatch-2-1504045122.jpg?crop=0.638xw:1.00xh;0.327xw,0&resize=980:*',
  'https://manofmany.com/wp-content/uploads/2023/07/14-Strongest-Celebrities-in-Hollywood.jpg',
  'https://i.pinimg.com/736x/d6/42/4f/d6424f277593a515430a44923fe3595d.jpg',
  'https://www.dmoose.com/cdn/shop/articles/1main_a2db1e23-aafb-4157-95ac-11a4d8a131cc.jpg?v=1652282285&width=800',
  'https://hips.hearstapps.com/hmg-prod/images/mh-8-4-train-like-1596571910.png?crop=0.423xw:0.846xh;0.0433xw,0.0128xh&resize=640:*',
  'https://manofmany.com/wp-content/uploads/2023/10/14-Strongest-Celebrities-in-Hollywood-Zac-Efron.jpg',
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