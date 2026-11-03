import {
  Camera, Heart, Droplets, LineChart, Moon, Play, Calendar, Brain, FlaskConical, Dumbbell, Move, Apple,
  Bed, Activity, Shield, Link2, User, Scissors, Sun, ListChecks, MessageCircle,
} from 'lucide-react'

// Plan 6.2: nawigacja w grupach, po polsku, z menu na telefonie (wcześniej 15+ pozycji w jednym rzędzie).
export const NAV_GROUPS = [
  {
    title: null,
    items: [
      { to: '/', label: 'Dziś', icon: Sun },
      { to: '/assistant', label: 'Asystent', icon: MessageCircle },
    ],
  },
  {
    title: 'Analiza',
    items: [
      { to: '/photos', label: 'Zdjęcia', icon: Camera },
      { to: '/analysis', label: 'Wyniki analizy', icon: Heart },
      { to: '/progress', label: 'Postęp', icon: LineChart },
      { to: '/style', label: 'Styl', icon: Scissors },
    ],
  },
  {
    title: 'Plan',
    items: [
      { to: '/recommendations', label: 'Rekomendacje', icon: Droplets },
      { to: '/skincare', label: 'Pielęgnacja', icon: Moon },
      { to: '/consistency', label: 'Regularność', icon: ListChecks },
      { to: '/experiments', label: 'Eksperymenty', icon: FlaskConical },
    ],
  },
  {
    title: 'Styl życia',
    items: [
      { to: '/training', label: 'Trening', icon: Dumbbell },
      { to: '/nutrition', label: 'Żywienie', icon: Apple },
      { to: '/sleep', label: 'Sen', icon: Bed },
      { to: '/stress', label: 'Stres', icon: Activity },
      { to: '/posture', label: 'Postawa', icon: Move },
    ],
  },
  {
    title: 'Więcej',
    items: [
      { to: '/videos', label: 'Wideo', icon: Play },
      { to: '/event', label: 'Przed wydarzeniem', icon: Calendar },
      { to: '/confidence', label: 'Pewność siebie', icon: Brain },
      { to: '/connections', label: 'Połączenia', icon: Link2 },
      { to: '/profile', label: 'Profil', icon: User },
      { to: '/privacy', label: 'Prywatność', icon: Shield },
    ],
  },
]
