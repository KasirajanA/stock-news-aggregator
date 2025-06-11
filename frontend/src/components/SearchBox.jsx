import { useState } from 'react';
import { TextField, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

const SearchBox = ({ onSearch }) => {
  const [searchText, setSearchText] = useState('');

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchText(value);
    onSearch(value);
  };

  return (
    <TextField
      placeholder="Search news..."
      value={searchText}
      onChange={handleSearchChange}
      size="small"
      fullWidth
      sx={{
        maxWidth: '300px',
        '& .MuiOutlinedInput-root': {
          backgroundColor: 'background.paper',
        }
      }}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <SearchIcon />
          </InputAdornment>
        ),
      }}
    />
  );
};

export default SearchBox; 