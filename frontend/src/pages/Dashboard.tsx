import React from 'react'
import { Box, Typography, Paper } from '@mui/material'

export const Dashboard: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography variant="body1">
          Welcome to the Hockey BI Dashboard. Here you can view an overview of your hockey data and analytics.
        </Typography>
      </Paper>
    </Box>
  )
}